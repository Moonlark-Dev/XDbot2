from .etm import data
from nonebot.params import CommandArg
from .su import su
from . import _error as error
import traceback
import os
import time

from nonebot.adapters.onebot.v11 import Message


@su.handle()
async def update(message: Message = CommandArg()):
    argument = str(message).split(" ")
    try:
        if argument[0] in ["update", "检查更新"]:
            data.save_data()
            await su.send("正在运行更新程序，请稍候 ...")
            old_branch = os.popen("git log").read().split("\n")[
                0].split(" ")[1][:7]
            os.system("python3 update.py")
            await su.send('旧提交：%s\n新提交：%s' % (old_branch, os.popen("git log").read().split("\n")[0].split(" ")[1][:7]))
        elif argument[0] in ["upgrade", "升级"]:
            data.save_data()
            await su.send("正在更新，请稍候 ...")
            old_branch = os.popen("git log").read().split("\n")[
                0].split(" ")[1][:7]
            os.system("python3 update.py")
            await su.send('旧提交：%s\n新提交：%s\n即将自动重启' % (old_branch, os.popen("git log").read().split("\n")[0].split(" ")[1][:7]))
            with open("data/reboot.py", "w") as f:
                f.write(str(time.time()))
    except BaseException:
        await error.report(traceback.format_exc(), su)
