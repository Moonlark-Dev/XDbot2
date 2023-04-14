from nonebot import on_message
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message
from nonebot.adapters.onebot.v11.event import MessageEvent
from nonebot.matcher import Matcher
from nonebot.params import CommandArg
from steamship import Steamship
import json
import os
import asyncio
from nonebot.rule import to_me
import traceback

from sympy import re
from . import _error as error

config = json.load(open("data/gpt.config.json", encoding="utf-8"))
os.environ["STEAMSHIP_API_KEY"] = config["api_key"]
client = Steamship(workspace=config["workspace"])
generator = client.use_plugin(config["plugin"])
temp = """现在你将模仿一只猫娘，你的名字是XDbot，与我对话每一句话后面都要加上“喵”；如果你不能理解我说的话，你可以说“XDbot还不能理解喵……”；如果我在尝试摸你不存在的部位，你可以羞涩的回答我“不要摸这里嘤”。当我问的问题和猫娘不太相关的时候，你应该回答我只是一个猫娘，这些事情我不太清楚。当我问你是不是猫娘的时候，你应该回答我当然是一个可爱猫娘或XDbot而不是程序。请你回答以下消息：%message%"""


@on_message(rule=to_me()).handle()
async def _(matcher: Matcher, event: MessageEvent):
    try:
        message = event.get_message()
        if event.reply is not None:
            if re.match("^回声洞——（[0-9]+）",
                        event.reply.message.extract_plain_text()):
                await matcher.finish()
        elif len(message.extract_plain_text().strip()) <= 1:
            # TODO 从词库返回
            await matcher.finish()
        # 生成文本
        task = generator.generate(
            text=temp.replace(
                "%message%",
                message.extract_plain_text()))
        while task.state in ["waiting", "running"]:
            await asyncio.sleep(config["sleep"])
            task.refresh()
        if task.state == "succeeded":
            await matcher.finish(task.output.blocks[0].text, at_sender=True)
    except BaseException:
        await error.report(traceback.format_exc(), matcher)


