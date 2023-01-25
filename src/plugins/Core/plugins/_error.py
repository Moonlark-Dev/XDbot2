#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
from nonebot import get_bots
from nonebot.internal.matcher.matcher import Matcher
import random

ctrlGroup = json.load(open("data/ctrl.json"))["control"]


async def report(err: str, matcher: any = None):
    bot = get_bots()[json.load(open("data/su.multiaccoutdata.ro.json"))[ctrlGroup]]
    await bot.send_group_msg(
        message = err,
        group_id = ctrlGroup)
    if matcher is not None:
        await matcher.send("处理失败", at_sender=True)
        if random.randint(1,4) == 1:
            await matcher.finish((
                "建议前往："
                "https://github.com/This-is-XiaoDeng/XDbot2/issues/new?assignees=&labels=%C2%B7+Bug&template=bug.yml"
                " 提交一个 Issue 反馈该问题"))

