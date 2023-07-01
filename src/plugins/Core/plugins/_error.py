#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import time
from nonebot.adapters.onebot.v11 import Message
import json
from nonebot import get_bots
import traceback
# from nonebot.exception import FinishedException
from nonebot.log import logger
# from nonebot.adapters.onebot.v11 import GroupMessageEvent, MessageEvent, MessageSegment
from nonebot.matcher import Matcher
# from nonebot.params import Matc
import os.path
import os
import sys

try:
    sys.path.append(os.path.abspath("src/plugins/Core/lib/md2img"))
    markdown2image = __import__("markdown2image")
except:
    pass

ctrlGroup = json.load(open("data/ctrl.json", encoding="utf-8"))["control"]
IGNORED_EXCEPTION = [
    "NetworkError",
    "IllegalQuantityException"
]
ehm = {}
ehm["errors"] = []
for file in os.listdir(os.path.abspath("src/plugins/Core/ehm")):
    try:
        data = json.load(open(os.path.join(os.path.abspath(
            "src/plugins/Core/ehm"), file), encoding="utf-8"))
        ehm["errors"][data.pop("match")] = data
    except:
        pass
ehm["unknown"] = json.load(open(os.path.join(os.path.abspath(
    "src/plugins/Core/ehm"), "unknown_error.json"), encoding="utf-8"))
ehm["templ"] = open(os.path.join(os.path.abspath(
    "src/plugins/Core/ehm"), "template.md"), encoding="utf-8").read()

# , event: MessageEvent | GroupMessageEvent | None = None):


async def report(_err: str | None = None, matcher: Matcher = Matcher(), event=None, feedback=True):
    err = _err or traceback.format_exc()
    error = err.splitlines()[-1]
    logger.debug(error)
    # 过滤错误
    if "FinishedException" in error and matcher is not None:
        await matcher.finish()
    # 反馈错误
    if err.startswith("Traceback"):
        # reply = MessageSegment.text("") if not event else MessageSegment.reply(event.message_id)
        if feedback:
            try:
                data = None
                for reg, _data in list(ehm["errors"].items()):
                    if re.match(reg, _err):
                        data = _data
                if not data:
                    data = ehm["unknown"]
                filename = f"data/_error.cache_{time.time()}.ro.png"
                markdown2image.md2img(
                    ehm["templ"].replace("%error%", err)
                    .replace("%because%", "- ".join(data["because"]))
                    .replace("%do%", "- ".join(data["do"]))
                    .replace("%log%", _err),
                    filename
                )
                await matcher.send(
                    Message(
                        f'[CQ:image,file=file://{os.path.abspath(filename)}]')
                )
                os.remove(filename)
            except:
                await matcher.send(f"处理失败！\n{error}", at_sender=True)

    # 过滤错误
    for e in IGNORED_EXCEPTION:
        if e in error:  # Issue #120
            return None
    # 上报错误
    bot = get_bots()[json.load(
        open("data/su.multiaccoutdata.ro.json", encoding="utf-8"))[ctrlGroup]]
    await bot.send_group_msg(message=err, group_id=ctrlGroup)
    if not err.startswith("Traceback"):
        return None
    logger.error(err)
    # 记录错误
    data = json.load(open("data/_error.count.json", encoding="utf-8"))
    data["count"] += 1
    json.dump(data, open("data/_error.count.json", "w", encoding="utf-8"))
