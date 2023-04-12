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
    for i in range(5):
        try:
            async with httpx.AsyncClient(proxies=openai.proxy) as client:
                response = await client.get("http://freeopenai.xyz/api.txt")
            api_keys = response.read().decode("utf-8").splitlines()
            logger.info(f"成功获取 {len(api_keys)} 个 API 密钥")
            return None
        except:
            logger.warning(f"获取 API 秘钥失败，将在 5s 后重试（{i} / 5）")
            await asyncio.sleep(5)
    logger.warning("无法获取 API 秘钥，使用内置")
    api_keys = [
        "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",
        "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",
        "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",
        "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",
        "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"
    ]

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
        
