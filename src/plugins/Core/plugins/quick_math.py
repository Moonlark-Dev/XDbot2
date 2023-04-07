import random
from traceback import format_exc
import asyncio
import traceback
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent
from nonebot.matcher import Matcher
from nonebot.params import CommandArg
from . import _lang as lang
from . import _error as error
from .etm import achievement, economy, exp
from nonebot_plugin_apscheduler import scheduler
from nonebot import get_bot, on_message, require, on_command
import json
from nonebot.log import logger
import time

require("nonebot_plugin_apscheduler")
group = None
answer = None
group_unanswered = {}
send_time = 0


def refresh_group_unanswered(groups=[]):
    global group_unanswered
    if not groups:
        groups = json.load(
            open(
                "data/quick_math.enabled_groups.json",
                encoding="utf-8"))
    for g in groups:
        group_unanswered[g] = 0


refresh_group_unanswered()


async def delete_msg(bot, message_id):
    global group, answer
    await asyncio.sleep(18)
    if None not in [group, answer]:
        await bot.delete_msg(message_id=message_id)
        group_unanswered[group] += 1
        group = None
        answer = None


@scheduler.scheduled_job("cron", minute="*/4", id="send_quick_math")
async def send_quick_math():
    global group, answer, send_time
    try:
        accout_data = json.load(
            open(
                "data/su.multiaccoutdata.ro.json",
                encoding="utf-8"))
        groups = json.load(
            open(
                "data/quick_math.enabled_groups.json",
                encoding="utf-8"))
        try:
            group = random.choice(groups)
        except BaseException:
            return None
        if group_unanswered[group] >= 3:
            return None
        question = f"{random.randint(0, 50)} {random.choice('+-*')} {random.randint(1, 50)}"
        answer = eval(question)
        bot = get_bot(accout_data[str(group)])
        send_time = time.time()
        msg_id = (await bot.send_group_msg(
            group_id=group,
            message=f"[QUICK MATH] {question} = ?"))["message_id"]
        asyncio.create_task(delete_msg(bot, msg_id))
    except BaseException:
        await error.report(format_exc())


@on_message().handle()
async def _(matcher: Matcher, event: GroupMessageEvent):
    global group, answer, send_time
    try:
        if group == event.group_id:
            if str(answer) in event.get_plaintext()\
                    and str(answer) != event.get_plaintext():
                data = json.load(open("data/quick_math.average.json", encoding="utf-8"))
                if time.time() - send_time <= data["average"] / 2:
                    group = None
                    answer = None
                    await matcher.send("[反作弊] 疑似发现外挂，本题无效")
    except:
        await error.report(traceback.format_exc())


@on_message().handle()
async def quick_math(matcher: Matcher, event: GroupMessageEvent):
    global group, answer, group_unanswered
    try:
        if group_unanswered[event.group_id] >= 3:
            group_unanswered[event.group_id] = int(random.choice("0122233333"))
    except BaseException:
        pass
    try:
        if event.group_id == group:
            try:
                _answ = int(event.get_plaintext().strip())
            except ValueError:
                await matcher.finish()

            if _answ == answer:
                group_unanswered[event.group_id] = 0
                add = [random.randint(1, 13), random.randint(1, 15)]
                economy.add_vi(event.get_user_id(), add[0])
                exp.add_exp(event.get_user_id(), add[1])
                await matcher.send(lang.text("quick_math.rightanswer", add, event.get_user_id()),
                                   at_sender=True)
                data = json.load(open("data/quick_math.average.json", encoding="utf-8"))
                data["average"] = round((data["average"] + (time.time() - send_time)) / 2, 3)
                json.dump(data, open("data/quick_math.average.json", "w", encoding="utf-8"))
                group = None
                answer = None
                achievement.increase_unlock_progress(
                    "我爱数学", event.get_user_id())

    except BaseException:
        await error.report(format_exc())


@on_command("quick-math", aliases={"qm"}).handle()
async def quick_math_command(matcher: Matcher, event: GroupMessageEvent):
    try:
        groups = json.load(
            open(
                "data/quick_math.enabled_groups.json",
                encoding="utf-8"))
        if event.group_id in groups:
            groups.pop(groups.index(event.group_id))
            await matcher.send(lang.text("quick_math.disable", [], event.get_user_id()))
        else:
            groups.append(event.group_id)
            await matcher.send(lang.text("quick_math.enable", [], event.get_user_id()))
        json.dump(
            groups,
            open(
                "data/quick_math.enabled_groups.json",
                "w",
                encoding="utf-8"))
        refresh_group_unanswered(groups)
    except BaseException:
        await error.report(format_exc(), matcher)

# [HELPSTART] Version: 2
# Command: qm
# Usage: qm
# Info: 开启/关闭速算
# [HELPEND]
