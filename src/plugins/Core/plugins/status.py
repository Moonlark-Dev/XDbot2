from nonebot.adapters.onebot.v11 import Message
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11.event import GroupMessageEvent
from nonebot.log import logger
from nonebot.adapters.onebot.v11.bot import Bot
from nonebot import on_message
from nonebot import on_command
from nonebot.adapters.onebot.v11.message import MessageSegment
import psutil
import os
import traceback
import json
import getpass
import time

status = on_command("status", aliases={"系统状态", "状态"})
ctrlGroup = json.load(open("data/ctrl.json", encoding="utf-8"))["control"]


@status.handle()
async def status_handle(bot: Bot):
    try:
       initData = json.load(open("data/init.json", encoding="utf-8"))
       psutilMemory = psutil.virtual_memory()
       await status.send(f"""系统状态：
CPU：{psutil.cpu_percent()}% ({int(psutil.cpu_freq().current / 1024 * 100 ) / 100}GHz)
内存：{int(psutilMemory.used / 1073741824 * 100) / 100}GiB / {int(psutilMemory.total / 1073741824 * 100) / 100}GiB ({psutilMemory.percent}%)
登录用户：{getpass.getuser()}
运行时间：{int(time.time() - initData['time']) / 60} min""")

    except BaseException:
        await bot.send_group_msg(
            message=traceback.format_exc(),
            group_id=ctrlGroup
        )


