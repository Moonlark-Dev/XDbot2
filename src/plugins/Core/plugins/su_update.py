from .etm import data
from nonebot.params import CommandArg
from .su import su
from . import _error as error
import traceback
import os
from .su_restart import _restart
from nonebot.adapters.onebot.v11 import Message


@su.handle()
async def update(message: Message = CommandArg()):
    argument = str(message).split(" ")
    try:
        if argument[0] in ["update", "检查更新"]:
            data.save_data()
            await su.send("正在运行更新程序，请稍候 ...")
            await su.finish(os.popen("git pull").read())
        elif argument[0] in ["upgrade", "升级"]:
            data.save_data()
            await su.send("正在更新，请稍候 ...")
            await su.send(os.popen("git pull").read())
            _restart()
    except BaseException:
        await error.report(traceback.format_exc(), su)
