#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import time
import traceback

from nonebot import on_command
from nonebot.adapters.onebot.v11 import Message
from nonebot.adapters.onebot.v11.bot import Bot
from nonebot.adapters.onebot.v11.event import GroupMessageEvent
from nonebot.exception import FinishedException
from nonebot.params import CommandArg

vote = on_command("vote", aliases={"投票"})
ctrlGroup = json.load(open("data/ctrl.json", encoding="utf-8"))['control']


@vote.handle()
async def voteHandle(
        bot: Bot,
        event: GroupMessageEvent,
        message: Message = CommandArg()):
    try:
        data = json.load(open("data/vote.data.json", encoding="utf-8"))
        argument = message.extract_plain_text().split("\n")
        group = event.get_session_id().split("_")[1]
        argument[0] = argument[0].split(" ")
        # 检查过期
        nowTime = time.time()
        length = 0
        _data = data.copy()
        for voteData in _data:
            if nowTime >= voteData["endTime"]:
                data[length]["status"] = "已结束"
            length += 1
        # 解析参数
        if argument[0][0] == "":
            text = "XDbot2 群投票列表：\n"
            length = 0
            for item in data:
                if item["group"] == group:
                    text += f"{length}. {item['title']}（{item['status']}）\n"
                length += 1
            await vote.finish(text)
        elif argument[0][0] == "create" or argument[0][0] == "创建":
            voteID = max(len(data) - 1, 0)
            if len(argument[0]) < 2:
                argument[0].append(24)
            else:
                argument[0][1] = int(argument[0][1])
            choices = []
            for c in argument[2:]:
                choices.append({"name": c, "user": []})
            data.append({
                "title": argument[1],
                "choices": choices,
                "sender": event.get_user_id(),
                "startTime": time.time(),
                "status": "进行中",
                "group": group,
                "endTime": time.time() + 60 * 60 * argument[0][1]
            })
            json.dump(data, open("data/vote.data.json", "w", encoding="utf-8"))
            await vote.finish(f"投票 #{voteID} 已创建")
        elif argument[0][0] == "view" or argument[0][0] == "查看":
            voteData = data[int(argument[0][1])]
            if event.get_session_id().split("_")[1] == voteData['group']:
                text = f"{voteData['title']}（{voteData['status']}）\n \n"
                length = 0
                selected = 0
                for c in voteData["choices"]:
                    selected += len(c['user'])
                for choice in voteData['choices']:
                    text += f"{length}. {choice['name']}（{len(choice['user'])}/{selected}）\n"
                    length += 1
                text += f" \n发起人：{(await bot.get_stranger_info(user_id=voteData['sender']))['nickname']}({voteData['sender']})"
                text += f"\n截止时间：{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}"
                await vote.finish(text)
            else:
                await vote.finish("权限不足")
        elif argument[0][0] == "select" or argument[0][0] == "选择":
            # 是否重复选择
            for c in data[int(argument[0][1])]["choices"]:
                if event.get_user_id() in c["user"]:
                    await vote.finish("您已经参与过了")
            # 选择
            if event.get_session_id().split("_")[1] == data[int(argument[0][1])]['group'] and voteData["status"] != "已结束":
                data[int(argument[0][1])]["choices"][int(
                    argument[0][2])]["user"].append(event.get_user_id())
                json.dump(data, open(
                    "data/vote.data.json", "w", encoding="utf-8"))
                await vote.finish("OK")
            else:
                await vote.finish("权限不足")

    except FinishedException:
        raise FinishedException()
    except IndexError:
        await vote.finish("投票不存在")
    except Exception:
        await bot.send_group_msg(
            message=traceback.format_exc(),
            group_id=ctrlGroup
        )

# [HELPSTART]
# !Usage 1 vote
# !Info 1 显示群投票列表（暂未完善，等待xd来改help）
# [HELPEND]