from nonebot.adapters.onebot.v11 import Message
from nonebot import on_command
from nonebot.matcher import Matcher
from nonebot.params import CommandArg
from . import _error
import traceback


@on_command("calc", aliases={"计算"}).handle()
async def run_calc(matcher: Matcher, message: Message = CommandArg()):
    try:
        await matcher.finish(str(eval(str(message))))
    except BaseException:
        await _error.report(traceback.format_exc(), matcher)
