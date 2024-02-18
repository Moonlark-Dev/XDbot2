from nonebot.adapters.onebot.v11 import Message
from nonebot import on_command
from nonebot.matcher import Matcher
from nonebot.params import CommandArg
from . import _error
import traceback
import math

def run_sandbox(code):
    env = {'__builtins__': None}
    for func in dir(math):
        env[func] = getattr(math, func)
    try:
        return eval(code, env)
    except Exception:
        return f"无法识别的表达式：{code}"

# [HELPSTART]
# !Usage 1 calc <表达式>
# !Info 1 计算表达式
# [HELPEND]


@on_command("calc", aliases={"计算"}).handle()
async def run_calc(matcher: Matcher, message: Message = CommandArg()):
    try:
        await matcher.finish(str(run_sandbox(str(message))))

    except BaseException:
        await _error.report(traceback.format_exc(), matcher)
