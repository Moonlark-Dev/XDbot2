#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
from nonebot import get_bots
import random
from . import _lang
ctrlGroup = json.load(open("data/ctrl.json"))["control"]


async def report(err: str, matcher: any = None):
    bot = get_bots()[
        json.load(
            open("data/su.multiaccoutdata.ro.json"))[ctrlGroup]]
    await bot.send_group_msg(
        message=err,
        group_id=ctrlGroup)
    if matcher is not None:
        await matcher.send(_lang.text("_error.failed"), at_sender=True)
        if random.randint(1, 4) == 1:
            await matcher.finish(_lang.text("_error.github",["https://github.com/This-is-XiaoDeng/XDbot2/issues/new?assignees=&labels=%C2%B7+Bug&template=bug.yml"]))
