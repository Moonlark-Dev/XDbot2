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


@get_driver().on_startup
async def get_apikeys():
    global api_keys
    while True:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get("http://freeopenai.xyz/api.txt")
            api_keys = response.read().decode("utf-8").splitlines()
            logger.info(f"成功获取 {len(api_keys)} 个 API 密钥")
            break
        except:
            logger.warning(f"获取 API 秘钥失败，将在 5s 后重试")
            await asyncio.sleep(5)
            


@on_command("gpt", aliases={"chat", "chatgpt"}).handle()
async def _(matcher: Matcher, event: GroupMessageEvent, message: Message = CommandArg()):
#     try:
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
    json.dump(messages, open("data/chatgpt.messages.json"))
        
