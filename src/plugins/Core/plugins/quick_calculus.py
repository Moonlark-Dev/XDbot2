from random import *
from traceback import format_exc
import asyncio
from sympy import *
from nonebot.adapters.onebot.v11 import GroupMessageEvent
from nonebot.matcher import Matcher
# from nonebot.params import CommandArg
from . import _lang as lang
from . import _error as error
from .etm import economy, exp
from nonebot_plugin_apscheduler import scheduler
from nonebot import get_bot, on_message, require, on_command
from nonebot.log import logger
import json
from sympy.parsing.sympy_parser import (
    parse_expr, standard_transformations, implicit_multiplication_application)

require("nonebot_plugin_apscheduler")
group = None
answer = None
group_unanswered = {}


def refresh_group_unanswered(groups=[]):
    global group_unanswered
    if not groups:
        groups = json.load(
            open(
                "data/quick_calculus.enabled_groups.json",
                encoding="utf-8"))
    for g in groups:
        group_unanswered[g] = 0


refresh_group_unanswered()


def generate_limit_question():
    x = symbols('x')
    f = choice([x**2 + 3*x - 2, x**3 - 2*x + 1,
               x**4 - 4*x**3 + 5*x**2 + 2*x - 1])
    a = randint(-10, 10)
    _limit = limit(f, x, a)
    question = f"计算函数 {latex(f)} 在 $x={a}$ 处的极限。"
    answer = f"{latex(_limit)}"
    return question, answer


def _check_answer(_answer, right_answer):
    transformations = standard_transformations + \
        (implicit_multiplication_application,)
    answer_expr = parse_expr(_answer, transformations=transformations)
    right_answer_expr = parse_expr(
        right_answer, transformations=transformations)
    return answer_expr == right_answer_expr


def check_answer(_answer, right_answer):
    try:
        return _check_answer(_answer, right_answer)
    except:
        return False


async def delete_msg(bot, message_id):
    global group, answer
    await asyncio.sleep(45)
    if None not in [group, answer]:
        await bot.delete_msg(message_id=message_id)
        group_unanswered[group] += 1
        group = None
        answer = None


@scheduler.scheduled_job("cron", minute="1/4", id="send_quick_calculus")
async def send_quick_calculus():
    global group, answer
    try:
        accout_data = json.load(
            open(
                "data/su.multiaccoutdata.ro.json",
                encoding="utf-8"))
        groups = json.load(
            open(
                "data/quick_calculus.enabled_groups.json",
                encoding="utf-8"))
        try:
            group = choice(groups)
        except BaseException:
            return None
        if group_unanswered[group] >= 3:
            return None
        # 生成问题
        if random() <= 0.5:
            x = Symbol('x')
            a = randint(1, 10)
            b = randint(1, 10)
            c = randint(1, 10)
            d = randint(1, 10)
            f = a*x**3 + b*x**2 + c*x + d
            if random() <= 0.5:
                # 求导数
                answer = str(diff(f, x)).replace(" ", "")
                question = f"求函数 f(x) = {f} 的导数"
                logger.debug(answer)
            else:
                answer = str(diff(diff(f, x), x)).replace(" ", "")
                question = f"求函数 f(x) = {f} 的二阶导数"
                logger.debug(answer)
        elif random() <= 0.25:
            x = Symbol('x')
            a = randint(1, 10)
            b = randint(1, 10)
            c = randint(1, 10)
            f = a*x**2 + b*x + c
            answer = str(diff(f, x)).replace(" ", "")
            question = f"求函数 f(x) = {f} 的导数"
            logger.debug(answer)
        else:
            question, answer = generate_limit_question()
            logger.debug(answer)

        bot = get_bot(accout_data[str(group)])
        msg_id = (await bot.send_group_msg(
            group_id=group,
            message=f"[QUICK CAICULUS] {question}"))["message_id"]
        asyncio.create_task(delete_msg(bot, msg_id))
    except BaseException:
        await error.report(format_exc())


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
                _answ = event.get_plaintext().strip().replace(" ", "")
            except ValueError:
                await matcher.finish()

            if check_answer(_answ, answer):
                group_unanswered[event.group_id] = 0
                add = [randint(10, 30), randint(5, 25)]
                economy.add_vi(event.get_user_id(), add[0])
                exp.add_exp(event.get_user_id(), add[1])
                await matcher.send(lang.text("quick_math.rightanswer", add, event.get_user_id()),
                                   at_sender=True)
                group = None
                answer = None
                # achievement.increase_unlock_progress(
                #     "我爱数学", event.get_user_id())

    except BaseException:
        await error.report(format_exc())


@on_command("quick-calculus", aliases={"qc"}).handle()
async def quick_math_command(matcher: Matcher, event: GroupMessageEvent):
    try:
        groups = json.load(
            open(
                "data/quick_calculus.enabled_groups.json",
                encoding="utf-8"))
        if event.group_id in groups:
            groups.pop(groups.index(event.group_id))
            await matcher.send(lang.text("quick_calculus.disable", [], event.get_user_id()))
        else:
            groups.append(event.group_id)
            await matcher.send(lang.text("quick_calculus.enable", [], event.get_user_id()))
        json.dump(
            groups,
            open(
                "data/quick_calculus.enabled_groups.json",
                "w",
                encoding="utf-8"))
        refresh_group_unanswered(groups)
    except BaseException:
        await error.report(format_exc(), matcher)

# [HELPSTART] Version: 2
# Command: qc
# Usage: qc
# Info: 开启/关闭快速微积分
# [HELPEND]
