from random import choice
import httpx
from nonebot import get_driver, logger, on_command
import json
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message
import openai
from nonebot.matcher import Matcher
from nonebot.params import CommandArg
import asyncio


api_keys = []
messages = json.load(open("data/chatgpt.messages.json", encoding="utf-8"))
openai.proxy = "http://127.0.0.1:7890"
openai.api_key = "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"

@on_command("gpt", aliases={"chat", "chatgpt"}).handle()
async def _(matcher: Matcher, event: GroupMessageEvent, message: Message = CommandArg()):
#     try:
        if str(event.group_id) not in messages.keys():
            messages[str(event.group_id)] = []
        messages[str(event.group_id)].append({"role": "user", "content": message.extract_plain_text()})
        openai.api_key = choice(api_keys)
        session = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=messages[str(event.group_id)])
        reply = session["choice"][0]["message"]
        messages[str(event.group_id)].append(reply)
        await matcher.finish(reply["content"])

@get_driver().on_shutdown
async def save_data():
    json.dump(messages, open("data/chatgpt.messages.json", "w", encoding="utf-8"))
        
