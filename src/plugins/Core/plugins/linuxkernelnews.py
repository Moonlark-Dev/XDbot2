from nonebot.adapters.onebot.v11.bot import Bot
# from nonebot.adapters.onebot.v11.event import MessageEvent
# from nonebot.adapters.onebot.v11 import Message
# from nonebot.params import CommandArg
from . import _error
from . import _lang
from nonebot.exception import FinishedException
from nonebot import on_command
from nonebot.adapters.onebot.v11 import (Bot, Message, MessageEvent)
import json
import traceback
import re
import httpx

ctrlGroup = json.load(open("data/ctrl.json", encoding="utf-8"))["control"]
linuxkernelnews = on_command("linuxkernelnews", aliases={"lkn"})


@linuxkernelnews.handle()
async def linuxkernelnewsHandle(bot: Bot,event: MessageEvent):
    try:
        async with httpx.AsyncClient() as client:
            req = await client.get("https://www.kernel.org/feeds/kdist.xml")
            data = req.read().decode("utf-8")
        data = re.findall(
            r'https://cdn.kernel.org/pub/linux/kernel/.*/linux-.*.tar.xz"', data)
        kernels = ""
        for i in range(len(data)):
            kernels += f"{i+1}. {data[i][:-1].replace('cdn.kernel.org/pub','mirrors.ustc.edu.cn/kernel.org')}\n"
        answer = f"""kernel.org {_lang.text('linuxkernelnews.new',[],event.get_user_id())}
{kernels}"""
        await linuxkernelnews.finish(answer)
    except FinishedException:
        raise FinishedException()
    except Exception:
        await _error.report(traceback.format_exc(), linuxkernelnews)

# [HELPSTART] Version: 2
# Command: lkn
# Usage: lkn
# Msg: 查看最新linux内核
# Info: linuxkernelnews（查看最新的linux内核）
# [HELPEND]
