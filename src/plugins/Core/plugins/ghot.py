import json
import traceback
from time import time
from datetime import date

from nonebot import require
from nonebot import on_command, on_message
from nonebot.exception import FinishedException
from nonebot.matcher import Matcher
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Bot, Message

from nonebot_plugin_apscheduler import scheduler

from . import _lang as lang
from . import _error as error


require("nonebot_plugin_apscheduler")

MINUTE = 60
HOUR = 3600


def update_stamps(data, filter_time, compress=False):
    pop_keys = []
    for group_id, stamps in data.items():
        new_stamps = list(filter(lambda x: time() - x < filter_time, stamps))
        if len(new_stamps) == 0:
            pop_keys.append(group_id)
        data[group_id] = len(new_stamps) if compress else new_stamps
    for group_id in pop_keys:
        data.pop(group_id)
    return data


@scheduler.scheduled_job("cron", minute="*", id="update_stamps")
async def _():
    data = json.load(open("data/ghot.stamps.json", encoding="utf-8"))
    data = update_stamps(data, HOUR)
    json.dump(data, open("data/ghot.stamps.json", "w", encoding="utf-8"))


@on_command("ghot", aliases={"群聊热度"}).handle()
async def _(bot: Bot, event: GroupMessageEvent, matcher: Matcher,
            arg: Message = CommandArg()):
    arg = str(arg).replace("-", "")
    try:
        if arg in ["", "m", "min"]:
            reply = lang.text("ghot.10min", [], event.get_user_id())
            data = json.load(open("data/ghot.stamps.json", encoding="utf-8"))
            data = update_stamps(data, 10 * MINUTE, True)

        elif arg in ["h", "hour"]:
            reply = lang.text("ghot.hour", [], event.get_user_id())
            data = json.load(open("data/ghot.stamps.json", encoding="utf-8"))
            data = update_stamps(data, HOUR, True)

        elif arg in ["d", "day"]:
            reply = lang.text("ghot.day", [], event.get_user_id())
            data = json.load(open("data/ghot.day.json", encoding="utf-8"))
            data.pop("date")

        elif arg in ["t", "total"]:
            reply = lang.text("ghot.total", [], event.get_user_id())
            data = json.load(open("data/ghot.total.json", encoding="utf-8"))

        else:
            await matcher.finish()

        sorted_data = sorted(data.items(), key=lambda x: x[1], reverse=True)
        n = 1
        for group_id, count in sorted_data[:10]:
            group_name = (await bot.get_group_info(group_id=int(group_id)))["group_name"]
            reply += f"{n}. {group_name}: {count}\n"
            n += 1
        reply += "-" * 30 + "\n"
        group_id = str(event.group_id)
        count = data[group_id]
        for i in range(len(sorted_data)):
            if sorted_data[i][0] == group_id:
                group_name = (await bot.get_group_info(group_id=int(group_id)))["group_name"]
                reply += f"{i + 1}. {group_name}: {count}"
                break
        await matcher.finish(reply)

    except BaseException:
        await error.report(traceback.format_exc(), matcher)


@on_message().handle()
async def _(event: GroupMessageEvent):
    try:
        data = json.load(open("data/ghot.stamps.json", encoding="utf-8"))
        if str(event.group_id) not in data.keys():
            data[str(event.group_id)] = []
        data[str(event.group_id)].append(time())
        json.dump(data, open("data/ghot.stamps.json", "w", encoding="utf-8"))

        data = json.load(open("data/ghot.day.json", encoding="utf-8"))
        if ("date" not in data.keys() or
                data["date"] != str(date.today())):
            data = {"date": str(date.today())}
        if str(event.group_id) not in data.keys():
            data[str(event.group_id)] = 0
        data[str(event.group_id)] += 1
        json.dump(data, open("data/ghot.day.json", "w", encoding="utf-8"))

        data = json.load(open("data/ghot.total.json", encoding="utf-8"))
        if str(event.group_id) not in data.keys():
            data[str(event.group_id)] = 0
        data[str(event.group_id)] += 1
        json.dump(data, open("data/ghot.total.json", "w", encoding="utf-8"))

    except BaseException:
        await error.report(traceback.format_exc())

# [HELPSTART] Version: 2
# Command: ghot
# Usage: ghot
# Usage: ghot-h
# Usage: ghot-d
# Usage: ghot-t
# Info: 获取最近10分钟、最近1小时、今日或总计的群聊热度
# Msg: 获取群聊热度
# [HELPEND]
