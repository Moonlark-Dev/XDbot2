from random import choice
import httpx
from nonebot import get_driver, logger, on_command
import json
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message

from nonebot.matcher import Matcher
from nonebot.params import CommandArg


api_keys = []
messages = json.load(open("data/chatgpt.messages.json", encoding="utf-8"))


@get_driver().on_startup
async def get_apikeys():
    global api_keys
    async with httpx.AsyncClient() as client:
        response = await client.get("http://freeopenai.xyz/api.txt")
    api_keys = response.read().decode("utf-8").splitlines()
    logger.info(f"成功获取 {len(api_keys)} 个 API 密钥")


@on_command("gpt", aliases={"chat", "chatgpt"}).handle()
async def _(matcher: Matcher, event: GroupMessageEvent, message: Message = CommandArg()):
#     try:
        messages[str(event.group_id)].append({"role": "user", "content": message.extract_plain_text()})
        # 发起请求
        data = {
            "messages": messages[str(event.group_id)],
            "max_length": 4096,
            "temperature": 0.7
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {choice(api_keys)}"
        }
        
        async with httpx.AsyncClient(proxy="http://127.0.0.1:7890") as client:
            response = await client.post(
                "https://api.openai.com/v1/gpt-3.5-turbo/generate",
                headers=headers,
                data=json.dumps(data)
            )
        await matcher.finish(str(response.json()))
