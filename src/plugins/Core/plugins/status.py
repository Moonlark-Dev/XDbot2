from nonebot.adapters.onebot.v11.bot import Bot
from nonebot import on_command
from nonebot.exception import FinishedException
import psutil
import os
import traceback
import json
import getpass
import time
import socket
import platform

status = on_command("status", aliases={"系统状态", "状态"})
ctrlGroup = json.load(open("data/ctrl.json", encoding="utf-8"))["control"]

async def cpu_percent(): return psutil.cpu_percent()
async def cpu_freq(): return f"{round(psutil.cpu_freq().current/1000,2)} Ghz / {round(psutil.cpu_freq().max/1000,2)} Ghz"
async def cpu_count(): return psutil.cpu_count()

async def mem_used(): return round(psutil.virtual_memory().used/1024/1024/1024, 1)
async def mem_total(): return round(psutil.virtual_memory().total/1024/1024/1024, 1)
async def mem_percent(): return psutil.virtual_memory().percent

async def swap_used(): return round(psutil.swap_memory().used/1024/1024/1024, 1)
async def swap_total(): return round(psutil.swap_memory().total/1024/1024/1024, 1)
async def swap_percent(): return psutil.swap_memory().percent

async def format_time(seconds):
    d = int(seconds/86400)
    h = int(seconds/3600) % 60
    m = int(seconds/60) % 60
    s = seconds % 60
    return f"{d}d{h}h{m}m{s}s"

async def uptime():
    try:
        seconds = int(float(open("/proc/uptime").read().split(' ')[0]))
    except:
        return 'Unknown'
    return format_time(seconds)

async def datetime(): return time.strftime("%Y/%m/%d %H:%M:%S", time.localtime())
async def user(): return getpass.getuser()
async def hostname(): return socket.gethostname()
async def os(): return platform.platform() 
async def pyver(): return platform.python_version()

@status.handle()
async def statusHandle(bot: Bot):
    try:
        initData = json.load(open("data/init.json", encoding="utf-8"))
        await status.finish(f"""系统状态：
CPU：({cpu_freq()} {cpu_count()}x {cpu_percent()})
内存：{mem_used()}GiB / {mem_total()}GiB ({mem_percent()}%)
交换内存：{swap_used()}GiB / {swap_total()}GiB ({swap_percent()}%)
运行时间：{format_time(int(time.time() - initData['time']))}
开机时间：{uptime()}
系统：{os()} ({user()}@{hostname()})
Python版本：{pyver()}""")
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
