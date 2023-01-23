#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import time
import traceback
import re

from nonebot_plugin_apscheduler import scheduler
from nonebot import on_command, require, get_bot
from nonebot.adapters.onebot.v11 import Message
from nonebot.adapters.onebot.v11.bot import Bot
from nonebot.adapters.onebot.v11.event import GroupMessageEvent
from nonebot.exception import FinishedException
from nonebot.params import CommandArg

require("nonebot_plugin_apscheduler")
vote = on_command("vote", aliases={"投票"})
ctrlGroup = json.load(open("data/ctrl.json", encoding="utf-8"))['control']


@vote.handle()
async def voteHandle(
        bot: Bot,
        event: GroupMessageEvent,
        message: Message = CommandArg()):
    try:
        data = json.load(open("data/vote.list.json", encoding="utf-8"))
        answer = ""
        argument = message.extract_plain_text().split("\n")
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
                "status": "进行中"
            }
            # 添加数据
            data[voteID] = voteData
            # 返回
            answer = "投票创建成功！ID: #{voteID}"
        elif mode == "list" or mode == "列表" or mode == "":
            answer = "XDbot2 投票列表：\n"
            for key in list(data.keys()):
                voteData = data[key]
                if voteData["group"] == event.group_id or voteData["global"]:
                    answer += f"[{key}] {voteData['title']} （{voteData['status']}）\n"
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
                answer += f"{length}. {c} （{selected}/{len(voteData['users'])}） {int(selected / len(voteData['user'] ) * 100)}%\n"

        elif mode == "select" or mode == "选择":
            voteData = data[argument[0].split(" ")[1]]
            choice = int(argument[0].split(" ")[2]) - 1
            if voteData['status'] == "进行中":
                if voteData["group"] == event.group_id or voteData["global"]:
                    if event.get_user_id() not in voteData["users"]:
                        data[argument[0].split(
                            " ")[1]]["users"][event.get_user_id()] = choice
                        answer = f"已选择：{voteData['choices'][choice]}"
                    else:
                        answer = "错误：不能重复投票"
                else:
                    answer = "错误：权限不足"
            else:
                answer = "错误：投票已结束"
        elif mode == "close" or mode == "结束":
            voteindex = argument[0].split(" ")[1]
            voteData = data[voteindex]
            if voteData['status'] == "进行中":
                voteData['status'] = "已结束"
                answer = f"结束了投票{voteindex}"
            else:
                answer = f"错误：投票{voteindex}已结束"
        elif mode == "delete" or mode == "删除":
            voteindex = argument[0].split(" ")[1]
            data.pop(voteindex)
            answer = f"投票{voteindex}已删除"
        json.dump(data, open("data/vote.list.json", "w", encoding="utf-8"))
        await vote.finish(str(answer))

    except FinishedException:
        raise FinishedException()
    except IndexError:
        await vote.finish("投票不存在")
    except Exception:
        await bot.send_group_msg(
            message=traceback.format_exc(),
            group_id=ctrlGroup
        )


@scheduler.scheduled_job("cron", minute="*/1", id="reloadVote")
async def reloadVote():
    data = json.load(open("data/vote.list.json", encoding="utf-8"))
    for key in list(data.keys()):
        voteData = data[key]
        bot = get_bot(str(voteData["bot"]))
        if voteData["status"] == "进行中":
            if time.time() >= voteData["endTime"]:
                await bot.send_group_msg(
                    message=f"投票「{voteData['title']}」已结束\n使用 /vote view {voteData['id']} 查看结果",
                    group_id=voteData["group"]
                )
                data[key]["status"] = "已结束"
            # 3600s，一小时
            elif int(voteData["endTime"] - time.time()) <= 3600 and "msg" not in voteData.keys():
                await bot.send_group_msg(
                    message=f"投票「{voteData['title']}」将在 1 小时后截止",
                    group_id=voteData["group"]
                )
                data[key]["msg"] = True
    json.dump(data, open("data/vote.list.json", "w", encoding="utf-8"))


# [HELPSTART]
# !Usage 1 vote
# !Info 1 群投票
# [HELPEND]
