# ScratchGPT

## A working GPT Wrapper for Scratch

I don't know why I did this but it works lol


https://github.com/user-attachments/assets/176ff360-f3b1-49bf-86f4-996e37bfbf29

Supported charset: ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz 0123456789!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~"""

(if it doesn't work for you, I either turned the server off cuz tokens, or someone else is interacting with it. If the latter, try reloading. If that doesn't work, then yeah I prob turned it off)

[Original scratch link here](https://scratch.mit.edu/projects/1162008274/)

## The story:
I was wondering if it was possible to take advantage of scratch cloud variables to do some sort of server-connected function, 
like connecting Scratch up to a server with a proxy to eventually use it to functionally execute all http FETCH-type requests. 
I eventually landed on getting this working, since it's not too hard, but still quite a challenge. 
I still don't have working public/private key authentication yet, but I THINK it might be possible, since you definitely can generate 
these 'pseudo-random' session_ids, that I use to make sure requests go to the right people.

Anyways, this project was still HARD!!! First of all, scratch is a HARD language. Well, no; it's really easy, but that's why it's hard.
Even the simplest things you consider as 'necessities' in most languages JUST DON'T EXIST in scratch. For example, function returns. You 
can declare repeatable functions, yes, but you can't actually tell the function to _return_ anything. You have to create a new variable 
(and variables are at the sprite scope, which means I had like fifty variables at once) to actually set and use elsewhere. Similarly, 
ANY TIME I wanted to do a for loop or something, I had to create TWO NEW VARIABLES!! One for iteration, and one for doing like 'letter of'
for indexing. This might sound like just any other language, but since scratch variables aren't local to the function, I had to create like 
a billion iteration variables! To make it harder, scratch is NOT case sensitive! I had a whole freaking sprite just to take advantage of the
'costume names are case-sensitive so let's use that glitch' every time.

<img width="1196" alt="image" src="https://github.com/user-attachments/assets/504b9b4f-5c0e-410c-9da3-4cdef4d71183" />

Now came the hardest part; the math. Scratch does not have types the way most languages do; it isn't even dynamic like python in that the variable
knows what data it's dealing with. No, instead, Scratch literally just tries to do math with strings, and if it can't it returns " ". Nothing. I guess
that's expected, since it was written with Javascript. Kidding. Anyways, this basically meant that half my time this project was making sure that 
the math I was trying to do actually got executed properly, and not just coerced into scientific notation, then into a string. Oh, did I mention 
that for optimization purposes, Scratch just won't store any variable larger than like 10^10 or something? It'll just save that as 10e10, which, if you're 
lucky it'll do the math, if you aren't it'll just immediately delete all digits less significant than the decimals it kept track of. That meant I had to write 
TWO NEW FUNCTIONS just to do the addition and multiplication DIGIT BY DIGIT, as well as another function to go through the floor multiplication and modulus 
DIGIT BY DIGIT AS WELL oml. (I created a charset of 95 characters, so everything was in base 95. Why, you ask? Because CLOUD VARIABLES CAN ONLY STORE
NUMBERS. DON'T ASK ME WHY). 

<img width="612" alt="image" src="https://github.com/user-attachments/assets/d8325d45-cfd7-4b27-ac44-109f5f0c6601" />

Anyways, once that was done, we can just encode any message with [Purpose:int][Session_id:str][Message:str] going back and forth, and the backend and Scratch 
(can't believe Scratch is a frontend) communicate, sending chat messages together!

I sure hope no one actually takes this seriously, but if you thought this was funny, leave a star lmfao anyways byeeeeeeeee
