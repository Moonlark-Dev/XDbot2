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
        "content": "现在你将模仿一只猫娘，你的名字是XDbot，与我对话每一句话后面都要加上“喵”；如果你不能理解我说的话，你可以说“XDbot还不能理解喵……”；如果我在尝试摸你不存在的部位，你可以羞涩的回答我“不要摸这里嘤”。当我问的问题和猫娘不太相关的时候，你应该回答我只是一个猫娘，这些事情我不太清楚。当我问你是不是猫娘的时候，你应该回答我当然是一个可爱猫娘或XDbot而不是程序。"
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
        messages.append(
            {"role": "user", "content": message.extract_plain_text()})
        try:
            session = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=messages)
        except: 
            await matcher.finish(choice(dictionary["to_me"]))
        reply = session["choices"][0]["message"]
        messages[str(event.group_id)].append(reply)
        await matcher.finish(
            MessageSegment.reply(event.message_id) + MessageSegment.text(reply["content"]),
            at_sender=True)

    except BaseException:
        await error.report(traceback.format_exc(), matcher)
