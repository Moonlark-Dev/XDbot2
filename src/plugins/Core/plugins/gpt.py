from nonebot import on_message
from nonebot.adapters.onebot.v11 import Message
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


@on_message(rule=to_me()).handle()
async def _(matcher: Matcher, event: MessageEvent):
    try:
        message = event.get_message()
        if event.reply is not None:
            if re.match("^回声洞——（[0-9]+）", event.reply.message.extract_plain_text()):
                await matcher.finish()
        elif len(message.extract_plain_text().strip()) <= 1:
            # TODO 从词库返回
            await matcher.finish()
        # 生成文本
        task = generator.generate(text=message.extract_plain_text())
        while task.state in ["waiting", "running"]:
            await asyncio.sleep(config["sleep"])
            task.refresh()
        if task.state == "succeeded":
            await matcher.finish(task.output.blocks[0].text, at_sender=True)
    except BaseException:
        await error.report(traceback.format_exc(), matcher)
