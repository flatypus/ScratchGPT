from flowchat import Chain, autodedent
from typing import Dict, List
from websockets.asyncio.client import connect
import asyncio
import dotenv
import json
import os
import pydantic

dotenv.load_dotenv()

CHARSET = """ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz 0123456789!"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~"""
SESSION_ID_LENGTH = 4
USERNAME = os.getenv("USERNAME")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

project_id = "1162008274"

url = "wss://clouddata.turbowarp.org"

variable = "☁ DATA"
data = None


async def connect_to_turbowarp():
    global data
    headers = {
        "User-Agent": "scratchgpt/1.0.0 https://github.com/flatypus/scratchgpt"
    }

    async def set_value(value):
        await websocket.send(json.dumps({
            "method": "set",
            "user": USERNAME,
            "project_id": project_id,
            "name": variable,
            "value": value
        }))

    async with connect(url, additional_headers=headers) as websocket:
        await websocket.send(json.dumps({
            "method": "handshake",
            "project_id": project_id,
            "user": USERNAME
        }))
        await set_value("")
        while True:
            message = await websocket.recv()
            message = json.loads(message)
            if "name" in message and message["name"] == variable:
                data = message["value"]
                print(f"Data set to: {data}")
                await on_set(data, set_value)
            await asyncio.sleep(1)


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
        result = CHARSET[number % base] + result
        number = number // base
    return filter_message(result)


async def on_set(value, set_value):
    if value == "":
        return
    number = str(int(value))
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

    if start_mode == "START" or session_id not in cache:
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
        chain = chain.link(
            message.content,
            assistant=message.role == "assistant"
        )
    response = chain.pull().last()
    print(f"Chatbot wants to respond with: {response}")
    cache[session_id].append(Message(role="assistant", content=response))
    # response to user from chatbot is encoded as mode 3
    response_encoded = f"{3}{encode(f'{session_id}{response}')}"
    print(f"Response encoded: {response_encoded}")
    await set_value(response_encoded)


asyncio.run(connect_to_turbowarp())
