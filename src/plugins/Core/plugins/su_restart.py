from nonebot.params import CommandArg
from traceback import format_exc
from .su import su
from .etm import data
from . import _error
from nonebot.adapters.onebot.v11 import Messagee

import sys
import os


def _restart() -> None:
    script = sys.argv[0]
    args = sys.argv[1:]
    os.execv(sys.executable, [sys.executable] + [script] + args)


@su.handle()
async def restart(message: Message = CommandArg()):
    argument = str(message).split(" ")
    try:
        # 保存数据
        data.save_data()
        if argument[0] in ["restart", "重新启动"]:
            # with open("data/reboot.py", "w") as f:
            #     f.write(str(time.time()))
            await su.send("重启命令已发出")
            _restart()
    except BaseException:
        await _error.report(format_exc(), su)
