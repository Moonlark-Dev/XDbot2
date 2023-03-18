#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
from nonebot import get_bots
import random
from nonebot.log import logger
from . import _lang

ctrlGroup = json.load(open("data/ctrl.json"))["control"]


async def report(err: str, matcher: any = None):
    error = err.splitlines()[-1]
    logger.debug(error)
    if "FinishedException" in error:
        return None
    bot = get_bots()[json.load(
        open("data/su.multiaccoutdata.ro.json"))[ctrlGroup]]
    await bot.send_group_msg(message=err, group_id=ctrlGroup)
    logger.error(err)
    if matcher is not None:
        await matcher.send(f"处理失败！\n{error}", at_sender=True)
        if random.random() <= 0.35:
            await matcher.finish(
                _lang.text(
                    "_error.github",
                    [
                        "https://github.com/This-is-XiaoDeng/XDbot2/issues/new?assignees=&labels=%C2%B7+Bug&template=bug.yml"
                    ],
                )
            )
