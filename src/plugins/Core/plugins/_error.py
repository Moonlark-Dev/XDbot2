#!/usr/bin/env python
# -*- coding: utf-8 -*-

# 自 2024 年
# 在重构此文件时浪费的时间:
# XiaoDeng3386: 1hr 53mins

import re
import time
from nonebot.adapters.onebot.v11 import Message
import json
from nonebot import get_bots
import traceback
from nonebot.log import logger
from nonebot.exception import RejectedException

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
IGNORED_EXCEPTION = ["NetWorkError", "IllegalQuantityException"]


def get_template() -> str:
    """获取错误处理手册模板

    Returns:
        str: 模板文件内容（未替换）
    """
    with open("src/plugins/Core/ehm/template.md", encoding="utf-8") as f:
        return f.read()


def _check_err_data_file(file_name: str) -> bool:
    """检查文件是否为错误数据文件

    Args:
        file_name (str): 文件名

    Returns:
        bool: 文件是否为错误数据文件
    """
    return (not file_name.startswith("_")) and file_name.endswith(".json")


def get_error_data(error_log: str) -> dict[str, str | list]:
    """获取错误数据

    Args:
        error_log (str): 异常日志

    Returns:
        dict[str, str|list]: EHM数据
    """
    for file in os.listdir("src/plugins/Core/ehm"):
        if not _check_err_data_file(file):
            continue
        with open(f"src/plugins/Core/ehm/{file}", encoding="utf-8") as f:
            ehm = json.load(f)
        if re.match(re.compile(ehm["match"], re.DOTALL), error_log):
            return ehm
    with open("src/plugins/Core/ehm/_unknown_error.json", encoding="utf-8") as f:
        return json.load(f)


async def report(
    _err: str | None = None, matcher: Matcher = Matcher(), event=None, feedback=True
) -> None:
    """Report a message

    Args:
        _err (str | None, optional): 上报的信息. Defaults to None.
        matcher (Matcher, optional): 当前事件触发器. Defaults to Matcher().
        event (_type_, optional): 不重要的参数，已弃用. Defaults to None.
        feedback (bool, optional): 是否对用户提示「处理失败」. Defaults to True.

    Returns:
        None: 无返回
    """
    err = _err or traceback.format_exc()
    error = err.splitlines()[-1]
    logger.debug(error)
    # 过滤错误
    if (
        ("finishedexception" in error.lower())
        or ("networkerror" in error.lower())
        and matcher is not None
    ):
        await matcher.finish()
    elif ("rejectedexception" in error.lower()):
        raise RejectedException
    # 反馈错误
    if err.startswith("Traceback"):
        if feedback:
            try:
                error_data = get_error_data(err)
                filename = f"data/_error.cache_{time.time()}.ro.png"
                markdown2image.md2img(
                    get_template()
                    .replace("%error%", error)
                    .replace("%because%", "\n".join(error_data["because"]))
                    .replace("%do%", "- " + "\n- ".join(error_data["do"]))
                    .replace("%log%", err),
                    filename,
                )
                await matcher.send(
                    Message(f"[CQ:image,file=file://{os.path.abspath(filename)}]"),
                    at_sender=True,
                )
                os.remove(filename)
            except:
                logger.warning(f"渲染图片失败：{traceback.format_exc()}")
                await matcher.send(f"处理失败！\n{error}", at_sender=True)

    # 过滤错误
    for e in IGNORED_EXCEPTION:
        if e in error:  # Issue #120
            return None
    # 上报错误
    bot = get_bots()[
        json.load(open("data/su.multiaccoutdata.ro.json", encoding="utf-8"))[ctrlGroup]
    ]
    await bot.send_group_msg(message=err, group_id=ctrlGroup)
    if not err.startswith("Traceback"):
        return None
    logger.error(err)
    # 记录错误
    error_data = json.load(open("data/_error.count.json", encoding="utf-8"))
    error_data["count"] += 1
    json.dump(error_data, open("data/_error.count.json", "w", encoding="utf-8"))
