from nonebot.adapters.onebot.v11.bot import Bot
from nonebot import on_command
from nonebot.exception import FinishedException
import psutil
import os
import traceback
import json
import getpass
import time

status = on_command("status", aliases={"系统状态", "状态"})
ctrlGroup = json.load(open("data/ctrl.json", encoding="utf-8"))["control"]


@status.handle()
async def statusHandle(bot: Bot):
    try:
        initData = json.load(open("data/init.json", encoding="utf-8"))
        psutilMemory = psutil.virtual_memory()
        psutilSwap = psutil.swap_memory()
        await status.finish(f"""系统状态：
CPU：{psutil.cpu_percent()}% ({int(psutil.cpu_freq().current / 1024 * 100 ) / 100}GHz)
内存：{int(psutilMemory.used / 1073741824 * 100) / 100}GiB / {int(psutilMemory.total / 1073741824 * 100) / 100}GiB ({psutilMemory.percent}%)
虚拟内存：{int(psutilSwap.used / 1073741824 * 100) / 100}GiB / {int(psutilSwap.total / 1073741824 * 100) / 100}GiB
系统类型：{os.name} （用户：{getpass.getuser()}）
运行时间：{int((time.time() - initData['time']) / 60 * 100) / 100} min""")

    except FinishedException:
        pass
    except Exception:
        await bot.send_group_msg(
            message=traceback.format_exc(),
            group_id=ctrlGroup)
        await status.finish("处理失败")

# [HELPSTART]
# !Usage 1 status
# !Info 1 查询XDbot2运行状态
# [HELPEND]
