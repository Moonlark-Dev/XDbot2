#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
from nonebot import get_bots
import random
from nonebot.exception import FinishedException
from nonebot.log import logger
# from nonebot.adapters.onebot.v11 import GroupMessageEvent, MessageEvent, MessageSegment
from nonebot.matcher import Matcher
from . import _lang

ctrlGroup = json.load(open("data/ctrl.json", encoding="utf-8"))["control"]
IGNORED_EXCEPTION = [
    "NetworkError",
    "IllegalQuantityException"
]


# , event: MessageEvent | GroupMessageEvent | None = None):
async def report(err: str, matcher: None | Matcher = None):
    error = err.splitlines()[-1]
    logger.debug(error)
    # 过滤错误
    if "FinishedException" in error:
        raise FinishedException()
    # 反馈错误
    if matcher is not None:
        # reply = MessageSegment.text("") if not event else MessageSegment.reply(event.message_id)
        await matcher.send(
            f"处理失败！\n{error}",
            at_sender=True)
        if random.random() <= 0.35:
            await matcher.send(
                _lang.text(
                    "_error.github",
                    [
                        "https://github.com/ITCraftDevelopmentTeam/XDbot2/issues/new?assignees=&labels=%C2%B7+Bug&template=bug.yml"
                    ],
                )
            )
    # 过滤错误
    for e in IGNORED_EXCEPTION:
        if e in error:  # Issue #120
            return None
    # 上报错误
    bot = get_bots()[json.load(
        open("data/su.multiaccoutdata.ro.json", encoding="utf-8"))[ctrlGroup]]
    await bot.send_group_msg(message=err, group_id=ctrlGroup)
    if "「" in err and matcher is None:
        return None
    logger.error(err)
    # 记录错误
    data = json.load(open("data/_error.count.json", encoding="utf-8"))
    data["count"] += 1
    json.dump(data, open("data/_error.count.json", "w", encoding="utf-8"))
