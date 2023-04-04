from nonebot.params import CommandArg
from traceback import format_exc
from .su import su
from .etm import data
from . import _error
from nonebot.adapters.onebot.v11 import Message
import time


@su.handle()
async def restart(message: Message = CommandArg()):
    argument = str(message).split(" ")
    try:
        # 保存数据
        data.save_data()
        if argument[0] in ["restart", "重新启动"]:
            with open("data/reboot.py", "w") as f:
                f.write(str(time.time()))
            await su.finish("重启命令已发出")
    except BaseException:
        await _error.report(format_exc(), su)
