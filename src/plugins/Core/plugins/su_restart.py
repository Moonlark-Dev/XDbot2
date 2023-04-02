from nonebot.params import CommandArg
from traceback import format_exc
from .su import su
from . import _error
import time


@su.handle()
async def restart(argument: list = str(CommandArg()).split(" ")):
    try:
        if argument[0] in ["restart", "重新启动"]:
            with open("data/reboot.py", "w") as f:
                f.write(str(time.time()))
            await su.finish("重启命令已发出")
    except BaseException:
        await _error.report(format_exc(), su)
