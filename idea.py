from typing import Dict, List
import dotenv
from flowchat import Chain, autodedent
import os
import scratchattach as sa
import warnings
import pydantic

warnings.filterwarnings('ignore', category=sa.LoginDataWarning)
dotenv.load_dotenv()

CHARSET = """ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz 0123456789!"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~"""
SESSION_ID_LENGTH = 4
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

project_id = "1162008274"

session = sa.login(USERNAME, PASSWORD)
cloud = session.connect_tw_cloud(project_id)
events = cloud.events()


class Message(pydantic.BaseModel):
    role: str
    content: str


cache: Dict[str, List[Message]] = {}


def filter_message(message: str):
    # make sure message only contains characters in CHARSET
    return "".join(char for char in message if char in CHARSET)


def encode(message: str):
    message = filter_message(message)
    base = len(CHARSET)
    number = 0
    for i, char in enumerate(message):
        number += (CHARSET.index(char) + 1) * (base ** (len(message) - i - 1))
    return number


def decode(number: int):
    base = len(CHARSET)
    result = ""
    while number > 0:
        print(CHARSET[number % base])
        result = CHARSET[number % base] + result
        number = number // base
    return filter_message(result)


@events.event
def on_set(activity):  # Called when a cloud var is set
    print(f"Variable {activity.var} was set to the value {activity.value}")
    number = str(int(activity.value))
    start_mode = None
    if number[0] == "1":
        start_mode = "START"
    elif number[0] == "2":
        start_mode = "MESSAGE"
    elif number[0] == "3":
        # should not respond to itself
        return

    number = int(number[1:])
    decoded = decode(number)
    session_id = decoded[:SESSION_ID_LENGTH]
    message = decoded[SESSION_ID_LENGTH:]

    print(f"Mode: {start_mode}, Session ID: {session_id}, Message: {message}")

    if start_mode == "START":
        cache[session_id] = []
    else:
        cache[session_id].append(Message(role="user", content=message))

    chain = (
        Chain("gpt-4o-mini")
        .anchor(autodedent(
            "You are a chatbot that can answer questions and help with tasks."
            f"Only respond in 1-2 sentences. You MAY ONLY use characters in {CHARSET}."
        ))
        .link("Hi! Can you tell me a bit about yourself?")
    )
    for message in cache[session_id]:
        chain = chain.link(message.role, message.content)
    response = chain.pull().last()
    print(f"Chatbot wants to respond with: {response}")
    cache[session_id].append(Message(role="assistant", content=response))
    # response to user from chatbot is encoded as mode 3
    cloud.set_var("DATA", f"{3}{encode(f'{session_id}{response}')}")


@events.event  # Called when the event listener is ready
def on_ready():
    print("Event listener ready!")


events.start()
