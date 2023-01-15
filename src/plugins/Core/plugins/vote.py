#!/usr/bin/env python
# -*- coding: utf-8 -*-

from nonebot import on_command
from nonebot.adapters.onebot.v11.bot import Bot
from nonebot.adapters.onebot.v11.event import GroupMessageEvent
from nonebot.adapters.onebot.v11 import Message
from nonebot.params import CommandArg
from nonebot.exception import FinishedException
import json
import time
import traceback

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
        argument[0] = argument[0].split(" ")
        if argument[0][0] == "":
            text = "XDbot2 群投票列表："
            length = 0
            for item in data:
                text += f"{length}. {item['title']}: {item['status']}"
            await vote.finish(text)
        elif argument[0][0] == "create" or argument[0][0] == "创建":
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
                "group": event.get_session_id().split("_")[1],
                "endTime": time.time() + 60 * 60 * argument[0][1]
            })
            json.dump(data, open("data/vote.data.json", "w", encoding="utf-8"))
            await vote.finish(f"投票 #{len(data) - 2} 已创建")
        elif argument[0][0] == "view" or argument[0][0] == "查看":
            voteData = data[int(argument[0][1])]
            if event.get_session_id().split("_")[1] == voteData['group']:
                text = f"（{voteData['status']}）{voteData['title']}\n \n"
                length = 0
                for choice in voteData['choices']:
                    text += f"{length}. {choice['name']}: {len(choice['user'])}\n"
                    length += 1
                text += f" \n发起人：{(await bot.get_stranger_info(user_id=voteData['sender']))['nickname']}({voteData['sender']})"
                await vote.finish(text)
            else:
                await vote.finish("权限不足")
        elif argument[0][0] == "select" or argument[0][0] == "选择":
            if event.get_session_id().split("_")[1] == data[int(argument[0][1])]['group']:
                data[int(argument[0][1])]["choices"][int(
                    argument[0][2])]["user"].append(event.get_user_id())
                json.dump(data, open(
                    "data/vote.data.json", "w", encoding="utf-8"))
                await vote.finish("OK")

    except FinishedException:
        raise FinishedException()
    except Exception:
        await bot.send_group_msg(
            message=traceback.format_exc(),
            group_id=ctrlGroup
        )
