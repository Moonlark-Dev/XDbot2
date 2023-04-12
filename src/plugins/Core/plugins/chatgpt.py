from traceback import format_exc
from nonebot import get_driver, on_command
import json
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message
from . import _error
import openai
from nonebot.matcher import Matcher
from nonebot.params import CommandArg

messages = json.load(open("data/chatgpt.messages.json", encoding="utf-8"))
openai.proxy = "http://127.0.0.1:7890"
openai.api_key = "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"


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
