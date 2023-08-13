#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import time
import traceback
import re
from . import _error
from . import _lang
from nonebot_plugin_apscheduler import scheduler
from nonebot import on_command, require, get_bot
from nonebot.adapters.onebot.v11 import Message
from nonebot.adapters.onebot.v11.bot import Bot
from nonebot.adapters.onebot.v11.event import GroupMessageEvent
from nonebot.exception import FinishedException
from nonebot.params import CommandArg

require("nonebot_plugin_apscheduler")
vote = on_command("vote", aliases={"投票"})
ctrlGroup = json.load(open("data/ctrl.json", encoding="utf-8"))["control"]


@vote.handle()
async def voteHandle(
    bot: Bot, event: GroupMessageEvent, message: Message = CommandArg()
):
    try:
        data = json.load(open("data/vote.list.json", encoding="utf-8"))
        answer = ""
        argument = str(message).split("\n")
        mode = argument[0].split(" ")[0]
        if mode == "create" or mode == "创建":
            # 收集数据
            timeMatch = re.search(r"[0-9]+h", argument[0])
            # 持续时间
            if timeMatch is not None:
                voteTime = int(timeMatch.group(0).replace("h", "")) * 60 * 60
            else:
                voteTime = 86400
            # 是否为投票全局
            if "global" in argument[0]:
                globalVote = True
                # group = None
            else:
                globalVote = False
            group = event.group_id
            # 选项列表
            choices = []
            for choice in argument[2:]:
                choices.append(choice)
            # 标题
            title = argument[1]
            # 发起人
            sender = event.get_user_id()
            # 开始、结束时间
            startTime = time.time()
            endTime = time.time() + voteTime
            # 投票ID
            length = 0
            while True:
                length += 1
                if str(length) not in data.keys():
                    voteID = str(length)
                    break
            # 汇总数据
            voteData = {
                "id": voteID,
                "global": globalVote,
                "group": group,
                "sender": sender,
                "startTime": startTime,
                "endTime": endTime,
                "choices": choices,
                "users": dict(),
                "bot": (await bot.get_login_info())["user_id"],
                "title": title,
                "status": "进行中",
            }
            # 添加数据
            data[voteID] = voteData
            # 返回
            answer = _lang.text("vote.create_success", [voteID], event.get_user_id())
        elif mode == "list" or mode == "列表" or mode == "":
            answer = _lang.text("vote.list_title", [], event.get_user_id())
            for key in list(data.keys()):
                voteData = data[key]
                if voteData["group"] == event.group_id or voteData["global"]:
                    answer += f"{key}. {voteData['title']} （{voteData['status']}）\n"
        elif mode == "view" or mode == "查看":
            voteData = data[argument[0].split(" ")[1]]
            answer = f"[{voteData['status']}] {voteData['title']}\n \n"
            length = 0
            for c in voteData["choices"]:
                selected = 0
                for k in voteData["users"].keys():
                    if voteData["users"][k] == length:
                        selected += 1
                length += 1
                answer += f"{length}. {c} （{selected}/{len(voteData['users'])}） {int(selected / max(len(voteData['users'] ), -1) * 100)}%\n"

        elif mode == "select" or mode == "选择":
            voteData = data[argument[0].split(" ")[1]]
            choice = int(argument[0].split(" ")[2]) - 1
            if voteData["status"] == "进行中":
                if voteData["group"] == event.group_id or voteData["global"]:
                    if event.get_user_id() not in voteData["users"]:
                        data[argument[0].split(" ")[1]]["users"][
                            event.get_user_id()
                        ] = choice
                        answer = _lang.text(
                            "vote.choice",
                            [voteData["choices"][choice]],
                            event.get_user_id(),
                        )
                    else:
                        answer = _lang.text(
                            "vote.error_repeat", [], event.get_user_id()
                        )
                else:
                    answer = _lang.text(
                        "vote.error_no_permission", [], event.get_user_id()
                    )
            else:
                answer = _lang.text("vote.error_end", [], event.get_user_id())
        elif mode == "close" or mode == "结束":
            voteindex = argument[0].split(" ")[1]
            voteData = data[voteindex]
            if voteData["status"] == "进行中":
                voteData["status"] = "已结束"
                answer = _lang.text("vote.end", [voteindex], event.get_user_id())
            else:
                answer = _lang.text("vote.ended", [voteindex], event.get_user_id())
        elif mode == "delete" or mode == "删除":
            voteindex = argument[0].split(" ")[1]
            data.pop(voteindex)
            answer = _lang.text("vote.delete", [voteindex], event.get_user_id())
        json.dump(data, open("data/vote.list.json", "w", encoding="utf-8"))
        await vote.finish(str(answer))

    except FinishedException:
        raise FinishedException()
    except IndexError:
        await vote.finish(_lang.text("vote.notfound", [], event.get_user_id()))
    except Exception:
        await _error.report(traceback.format_exc(), vote)


async def reloadVote():
    data = json.load(open("data/vote.list.json", encoding="utf-8"))
    accouts = json.load(open("data/su.multiaccoutdata.ro.json", encoding="utf-8"))
    for key in list(data.keys()):
        voteData = data[key]
        bot = get_bot(accouts[str(voteData["group"])])
        if voteData["status"] == "进行中":
            if time.time() >= voteData["endTime"]:
                await bot.send_group_msg(
                    message=_lang.text(
                        "vote.time_end", [voteData["title"], voteData["id"]]
                    ),
                    group_id=voteData["group"],
                )
                data[key]["status"] = "已结束"
            # 3600s，一小时
            elif (
                int(voteData["endTime"] - time.time()) <= 3600
                and "msg" not in voteData.keys()
            ):
                await bot.send_group_msg(
                    message=_lang.text("vote.time_1h_end", [voteData["title"]]),
                    group_id=voteData["group"],
                )
                data[key]["msg"] = True
    json.dump(data, open("data/vote.list.json", "w", encoding="utf-8"))


@scheduler.scheduled_job("cron", minute="*/1", id="reloadVote")
async def reload_task():
    try:
        await reloadVote()
    except Exception:
        await _error.report(traceback.format_exc())


# [HELPSTART]
# !Usage 1 vote
# !Info 1 群投票
# [HELPEND]
