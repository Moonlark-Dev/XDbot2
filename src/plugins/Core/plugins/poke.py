from random import random
import traceback
from nonebot import on_command
import asyncio
from nonebot.adapters.onebot.v11 import Message
from . import _error
from nonebot.matcher import Matcher
from nonebot.params import CommandArg


@on_command("poke").handle()
async def poke(matcher: Matcher, message: Message = CommandArg()):
    try:
        argv = message.extract_plain_text().split(" ")
        for _ in range(min(15, int(argv[1]))):
            await matcher.send(Message(f"[CQ:poke,qq={argv[0]}]"))
            await asyncio.sleep(1 + random())
    except:
        await _error.report(traceback.format_exc(), matcher)
