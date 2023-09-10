#!/usr/bin/env python
# -*- coding: utf-8 -*-

from nonebot.adapters.onebot.v11.bot import Bot
from nonebot.adapters.onebot.v11.event import GroupMessageEvent
from nonebot.exception import FinishedException
from nonebot import on_command, on_message
import json
import traceback
import time
import re
from . import _lang

whoAtme = on_command(
    "whoAtMe",
    aliases={"whoAtme", "whoatme", "wam", "谁At我", "又有没妈的At我了？", "哪个傻逼At我", "谁他妈At我"},
)
whoAtmeWriter = on_message()
ctrlGroup = json.load(open("data/ctrl.json", encoding="utf-8"))["control"]

# [HELPSTART]
# !Usage 1 wam
# !Info 1 谁At我
# [HELPEND]


@whoAtme.handle()
async def whoAtmd(bot: Bot, event: GroupMessageEvent):
    try:
        data = json.load(open(f"data/whoAtme.data.json", encoding="utf-8"))
        userData = data[event.get_user_id()]
        try:
            groupData = data[event.get_user_id()].pop(str(event.group_id))
        except KeyError:
            groupData = []
        forwardMessage = [
            {
                "type": "node",
                "data": {
                    "name": _lang.text("whoAtme.notice", [], event.get_user_id()),
                    "uin": (await bot.get_login_info())["user_id"],
                    "content": _lang.text("whoAtme.title", [], event.get_user_id()),
                },
            }
        ]
        # 倒过来
        messages = []
        for d in groupData:
            messages.insert(0, d)
        # 合成
        for messageID in messages:
            forwardMessage.append({"type": "node", "data": {"id": messageID}})
        # 发送
        await bot.send_group_forward_msg(
            messages=forwardMessage, group_id=event.group_id
        )
        # 查询其他数据
        otherAtCount = 0
        otherGroupCount = len(userData.keys())
        for otherGroup in userData:
            otherAtCount += len(otherGroup)
        # 结束处理
        if otherAtCount:
            await whoAtme.send(
                _lang.text(
                    "whoAtme.other",
                    [otherAtCount, otherGroupCount],
                    event.get_user_id(),
                )
            )
        json.dump(data, open("data/whoAtme.data.json", "w", encoding="utf-8"))
        await whoAtme.finish()

    except FinishedException:
        raise FinishedException()
    except Exception:
        await bot.send_group_msg(message=traceback.format_exc(), group_id=ctrlGroup)
        await whoAtme.finish(_lang.text("whoAtme.error", [], event.get_user_id()))


@whoAtmeWriter.handle()
async def whoAtmdWriterHandle(bot: Bot, event: GroupMessageEvent):
    try:
        data = json.load(open("data/whoAtme.data.json", encoding="utf-8"))
        message = str(event.get_message())
        msgID = event.message_id
        # print(message)
        match = re.search("\\[CQ:at,qq=[0-9]+\\]", message)
        # print(match)
        if match:
            qq = match.group(0).replace("[CQ:at,qq=", "").replace("]", "")
            try:
                if len(data[qq][str(event.group_id)]) >= 98:
                    data[qq][str(event.group_id)].pop(0)
                data[qq][str(event.group_id)].append(msgID)

            except Exception:
                try:
                    data[qq][str(event.group_id)] = [msgID]
                except Exception:
                    data[qq] = {str(event.group_id): [msgID]}
            json.dump(data, open("data/whoAtme.data.json", "w", encoding="utf-8"))

    except Exception:
        await bot.send_group_msg(message=traceback.format_exc(), group_id=ctrlGroup)
