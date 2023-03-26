import random
from traceback import format_exc
import asyncio
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent
from nonebot.matcher import Matcher
from nonebot.params import CommandArg
from . import _lang as lang
from . import _error as error
from .etm import achievement, economy, exp
from nonebot_plugin_apscheduler import scheduler
from nonebot import get_bot, on_message, require, on_command
import json

require("nonebot_plugin_apscheduler")
group = None
answer = None


async def delete_msg(bot, message_id):
    global group, answer
    await asyncio.sleep(10)
    if None not in [group, answer]:
        await bot.delete_msg(message_id=message_id)
        group = None
        answer = None

@scheduler.scheduled_job("cron", minute="*/4", id="send_quick_math")
async def send_quick_math():
    global group, answer
    try:
        accout_data = json.load(
            open(
                "data/su.multiaccoutdata.ro.json",
                encoding="utf-8"))
        groups = json.load(
            open(
                "data/quick_math.enabled_groups.json",
                encoding="utf-8"))
        group = random.choice(groups)
        question = f"{random.randint(0, 50)} {random.choice('+-*')} {random.randint(1, 50)}"
        answer = eval(question)
        bot = get_bot(accout_data[str(group)])
        msg_id = (await bot.send_group_msg(
            group_id=group,
            message=f"[QUICK MATH] {question} = ?"))["message_id"]
        asyncio.create_task(delete_msg(bot, msg_id))
    except BaseException:
        await error.report(format_exc())


@on_message().handle()
async def quick_math(matcher: Matcher, event: GroupMessageEvent):
    global group, answer
    try:
        if event.group_id == group:
            try:
                _answ = int(event.get_plaintext().strip())
            except ValueError:
                await matcher.finish()

            if _answ == answer:
                add = [random.randint(1, 13), random.randint(1, 15)]
                economy.add_vi(event.get_user_id(), add[0])
                exp.add_exp(event.get_user_id(), add[1])
                await matcher.send(lang.text("quick_math.rightanswer", add, event.get_user_id()),
                                   at_sender=True)
                group = None
                answer = None

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
    except BaseException:
        await error.report(format_exc(), matcher)
