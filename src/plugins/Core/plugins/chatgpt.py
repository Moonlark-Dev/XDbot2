from traceback import format_exc
from nonebot import get_driver, on_command
import json
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message, MessageEvent
from . import _error
import openai
from nonebot.matcher import Matcher
from nonebot.params import CommandArg

messages = json.load(open("data/chatgpt.messages.json", encoding="utf-8"))
config = json.load(open("data/chatgpt.config.json", encoding="utf-8"))
openai.proxy = config["proxy"]
openai.api_key = config["api_key"]


@on_command("gpt-config").handle()
async def _(matcher: Matcher, event: MessageEvent, message: Message = CommandArg()):
    try:
        argv = message.extract_plain_text().split(" ")
        if argv[0] == "proxy":
            if len(argv) == 1:
                await matcher.finish(str(openai.proxy))
            else:
                openai.proxy = argv[1]
                config["proxy"] = argv[1]
                await matcher.finish(f"代理已设为：{argv[1]}")
        elif argv[0] == "apikey":
            if len(argv) == 1:
                await matcher.finish(str(openai.api_key))
            else:
                openai.api_key = argv[1]
                config["api_key"] = argv[1]
                await matcher.finish(f"API 秘钥已设为：{argv[1]}")



@on_command("gpt", aliases={"chat", "chatgpt"}).handle()
async def _(matcher: Matcher, event: GroupMessageEvent, message: Message = CommandArg()):
    try:
        if str(event.group_id) not in messages.keys():
            messages[str(event.group_id)] = []
        messages[str(event.group_id)].append(
            {"role": "user", "content": message.extract_plain_text()})
        session = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=messages[str(event.group_id)])
        reply = session["choices"][0]["message"]
        messages[str(event.group_id)].append(reply)
        await matcher.finish(reply["content"], at_sender=True)
    except BaseException:
        await _error.report(format_exc(), matcher)


@get_driver().on_shutdown
async def save_data():
    json.dump(
        messages,
        open(
            "data/chatgpt.messages.json",
            "w",
            encoding="utf-8"))
    json.dump(config, open("data/chatgpt.config.json", "w", encoding="utf-8"))
