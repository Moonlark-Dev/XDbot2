from nonebot.adapters.onebot.v11 import Message
from lupa import LuaRuntime
from nonebot import on_command
from nonebot.matcher import Matcher
from nonebot.params import CommandArg
from . import _error
import traceback

lua = LuaRuntime(unpack_returned_tuples=True)
lua.require("src.plugins.Core.lua.calc")
run_sandbox = lua.eval("run_sandbox")


@on_command("calc", aliases={"计算"}).handle()
async def run_calc(matcher: Matcher, message: Message = CommandArg()):
    try:
        await matcher.finish(str(run_sandbox(str(message))))

    except BaseException:
        await _error.report(traceback.format_exc(), matcher)

