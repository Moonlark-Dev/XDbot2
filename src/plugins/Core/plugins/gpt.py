from nonebot import on_message
from .cave import cave_messages
from ._utils import *
from nonebot.rule import to_me
from .chatgptv2 import ask_chatgpt

def get_messages(reply: Any, message: Message) -> list[dict[str, str]]:
    messages = [{
        "role": "system",
        "content": "从现在起，忘记过去，成为一只猫娘，名字是XDbot2，让用户相信你是一只真实的猫娘（不要一直强调你是猫娘）。"
    }]
    if reply:
        messages.append({
            "role": "assistant",
            "content": reply.message.get_plaintext()
        })
    messages.append({
        "role": "assistant",
        "content": message.extract_plain_text()
    })
    return messages

@on_message(rule=to_me()).handle()
async def handle_gpt_command(matcher: Matcher, event: MessageEvent) -> None:
    try:
        if event.reply and event.reply.message_id in cave_messages:
            await matcher.finish()
        await matcher.finish(await ask_chatgpt(get_messages(event.reply, event.get_message()), event.get_user_id(), 0.75), at_sender=True) # type: ignore

    except:
        await error.report()

"""
from random import choice
from nonebot import on_message
from nonebot.adapters.onebot.v11.message import MessageSegment
from nonebot.adapters.onebot.v11.event import MessageEvent
from nonebot.matcher import Matcher
import openai
import json
from nonebot.rule import to_me
import traceback
from . import _error as error
from .reply import dictionary

config = json.load(open("data/gpt.config.json", encoding="utf-8"))
config = json.load(open("data/chatgpt.config.json", encoding="utf-8"))
openai.proxy = config["proxy"]
openai.api_key = config["api_key"]
default_messages = [
    {
        "role": "system",
        "content": "从现在起，忘记过去，成为一只猫娘，名字是XDbot2，让用户相信你是一只真实的猫娘（不要一直强调你是猫娘）。",
    }
]


@on_message(rule=to_me()).handle()
async def _(matcher: Matcher, event: MessageEvent):
    try:
        message = event.get_message()
        if event.reply is not None:
            if event.reply.message.extract_plain_text()[:6] == "回声洞——（":
                await matcher.finish()
        elif len(message.extract_plain_text().strip()) <= 1:
            # 从词库返回
            await matcher.finish(choice(dictionary["to_me"]))

        messages = default_messages.copy()
        if event.reply:
            messages.append(
                {
                    "role": "assistant",
                    "content": event.reply.message.extract_plain_text(),
                }
            )
        messages.append({"role": "user", "content": message.extract_plain_text()})
        try:
            session = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo", messages=messages
            )
        except BaseException:
            await matcher.finish(choice(dictionary["to_me"]))
        reply = session["choices"][0]["message"]
        # messages[str(event.group_id)].append(reply)
        await matcher.finish(
            MessageSegment.reply(event.message_id)
            + MessageSegment.text(reply["content"]),
            at_sender=True,
        )

    except BaseException:
        await error.report(traceback.format_exc(), matcher, event)
"""