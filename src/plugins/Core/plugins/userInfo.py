#!/usr/bin/env python
# -*- coding: utf-8 -*-

from nonebot.adapters.onebot.v11.bot import Bot
from nonebot.adapters.onebot.v11.event import MessageEvent
from nonebot.exception import FinishedException
from nonebot import on_command
import time
import traceback
import json
from . import _lang

userInfo = on_command(
    "user-info",
    aliases={
        "userinfo",
        "info",
        "爷的信息",
        "userInfo"})
ctrlGroup = json.load(open("data/ctrl.json"))["control"]


@userInfo.handle()
async def userInfoHandle(bot: Bot, event: MessageEvent):
    try:
        data = json.load(open("data/etm.userData.json"))[event.get_user_id()]
        # 等级进度条
        bar = ""
        for _ in range(int(data['exp'] / (data['level'] ** 2) * 10)):
            bar += "="
        for _ in range(10 - int(data['exp'] / (data['level'] ** 2) * 10)):
            bar += "  "
        # VIP
        if data['vip']['level'] is None:
            vip = _lang.text("userInfo.no_vip", [], event.get_user_id())
            endTime = "???"
        else:
            vip = "VIP" + "+" * data['vip']['level'] + \
                f" ({data['vip']['level']})"
            if data['vip']["endTime"] is None:
                endTime = _lang.text(
                    "userInfo.per_vip", [], event.get_user_id())
            else:
                endTime = time.strftime(
                    "%Y-%m-%d",
                    time.localtime(
                        data['vip']['endTime']))

        reply = (
            f"+-----「{_lang.text('userInfo.title',[],event.get_user_id())}」-----+\n"
            f"  {(await bot.get_stranger_info(user_id=event.get_user_id()))['nickname']}({event.get_user_id()})\n \n"
            f"  {_lang.text('userInfo.level',[],event.get_user_id())}Lv{data['level']}（{data['exp']} / {data['level'] ** 2}）\n"
            f"    [{bar}]\n"
            f"  {_lang.text('userInfo.vip',[],event.get_user_id())}{vip}\n"
            f"    {_lang.text('userInfo.endtime',[],event.get_user_id())}{endTime}\n"
            "+-------------------------+")
        await userInfo.finish(reply)

    except FinishedException:
        raise FinishedException()
    except Exception:
        await bot.send_group_msg(
            message=traceback.format_exc(),
            group_id=ctrlGroup
        )
        await userInfo.finish(_lang.text("userInfo.error", [], event.get_user_id()))
