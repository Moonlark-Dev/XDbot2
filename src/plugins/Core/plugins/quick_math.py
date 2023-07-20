import random
import lupa
from traceback import format_exc
import asyncio
import traceback
from nonebot.adapters.onebot.v11 import GroupMessageEvent, MessageSegment
from nonebot.matcher import Matcher
from . import _lang as lang
from sympy import Symbol, Eq, solve, latex
from . import _error as error
from .etm import achievement, economy, exp
from nonebot.permission import SUPERUSER
from nonebot_plugin_apscheduler import scheduler
from nonebot import get_bot, on_message, require, on_command, on_regex
import json
from PIL import Image, ImageDraw, ImageFont
import time
from io import BytesIO
from lupa import LuaRuntime
import re

require("nonebot_plugin_apscheduler")
group = None
answer = None
group_unanswered = {}
send_time = 0
lua = LuaRuntime(unpack_returned_tuples=True)
lua.require("src.plugins.Core.lua.calc")
run_sandbox = lua.eval("run_sandbox")

eggs = {
    "0/0=?": "regex>[iI][nN][fF]([iI][nN][iI][tT][yY])?|[nN]a[nN]|ZeroDivisionError",
    "creeper?": "regex>[aA][wW]+(.*?)[mM][aA][N](.*?)",
    "undefined+undefined=?": "regex>[iI][nN][fF]([iI][nN][iI][tT][yY])?|[nN][aA][nN]|[uU][nN][dD][fF][iI][nN][eE][dD]",
    "114+514=?": "regex>哼啊+|114|514|114514|1919|810|1919810"
}


def generate_equation():
    x = Symbol('x')
    a, b = random.randint(1, 10), random.randint(1, 10)
    eq = Eq(a * x + b, random.randint(1, 50))
    ans = solve(eq)
    return eq, ans


def render_text_as_image(_string):
    global answer
    string = _string.replace(" ", "")
    # 处理彩蛋，https://github.com/ITCraftDevelopmentTeam/XDbot2/pull/291
    if random.random() <= 0.03:
        string, answer = random.choice(list(eggs.items()))
    # Set the font size and the font type
    font_size = 20, 16
    font = ImageFont.truetype(
        "./src/plugins/Core/font/HYRunYuan-55W.ttf", font_size[0])
    title_font = ImageFont.truetype(
        "./src/plugins/Core/font/HYRunYuan-55W.ttf", font_size[1])
    # Get the size of the text
    width1, height1 = font.getsize(string)
    width2, height2 = title_font.getsize("[QUICK MATH]")
    # Create a new image with the size of the text
    image = Image.new('RGB', (max(width1, width2), max(
        height1, height2) + 18), color='white')
    # Draw the text on the image
    draw = ImageDraw.Draw(image)
    draw.text((0, 17), string, fill='black', font=font)
    draw.text((0, 0), "[QUICK MATH]", fill='black', font=title_font)
    # Remove any extra white space in the image
    bbox = image.getbbox()
    image = image.crop(bbox)
   # # Save the image to the local system
   # image.save('data/quick_math.image.png')
    io = BytesIO()
    image.save(io, format="PNG")
    return io.getvalue()


# render_text_as_image("[QUICK MATH] 29 + 1 = ?")


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


@on_command("new-quick-math", aliases={"nqm"}, permission=SUPERUSER).handle()
async def _(matcher: Matcher, event: GroupMessageEvent):
    global group, answer, send_time
    try:
        accout_data = json.load(
            open(
                "data/su.multiaccoutdata.ro.json",
                encoding="utf-8"))
        group = event.group_id
        if random.random() <= 0.5:
            question = f"{random.randint(0, 40)} {random.choice('+-*')} {random.randint(0, 35)}"
            answer = eval(question)
            question += " = ?"
        else:
            question, answer = generate_equation()
            question = latex(question)
            answer = str(answer).replace("[", "").replace("]", "")
        bot = get_bot(accout_data[str(group)])
        send_time = time.time()
        msg_id = (await bot.send_group_msg(
            group_id=group,
            message=MessageSegment.image(render_text_as_image(f"{question}"))))["message_id"]
        await asyncio.sleep(20)
        if None not in [group, answer]:
            await bot.delete_msg(message_id=msg_id)
            group_unanswered[group] += 1
            group = None
            answer = None
    except BaseException:
        await error.report(format_exc())


@scheduler.scheduled_job("cron", minute="*/2", id="send_quick_math")
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
        if group_unanswered[group] >= 2:
            return None
        if random.random() <= 0.5:
            question = f"{random.randint(0, 40)} {random.choice('+-*')} {random.randint(0, 35)}"
            answer = eval(question)
            question += " = ?"
        else:
            question, answer = generate_equation()
            question = latex(question)
            answer = str(answer).replace("[", "").replace("]", "")
        bot = get_bot(accout_data[str(group)])
        send_time = time.time()
        msg_id = (await bot.send_group_msg(
            group_id=group,
            message=MessageSegment.image(render_text_as_image(f"{question}"))))["message_id"]
        await asyncio.sleep(20)
        if None not in [group, answer]:
            await bot.delete_msg(message_id=msg_id)
            group_unanswered[group] += 1
            group = None
            answer = None
    except BaseException:
        await error.report()


def test_regex(pattern: str, string: str) -> bool:
    if pattern.startswith("regex>"):
        pattern = pattern[6:]
        return bool(re.match(f"^({pattern})$", string.strip()))
    return False


"""
@on_message().handle()
async def _(matcher: Matcher, event: GroupMessageEvent):
    global group, answer, send_time
    try:
        if group == event.group_id:
            _answ = event.get_plaintext()
            if (test_regex(_answ, answer)
                    or (str(answer) in _answ and str(answer) != _answ)):
                data = json.load(
                    open("data/quick_math.average.json", encoding="utf-8"))
                if time.time() - send_time <= data["average"] / 2:
                    group = None
                    answer = None
                    await matcher.send("[反作弊] 疑似发现外挂，本题无效")
    except BaseException:
        await error.report(traceback.format_exc())
"""


@on_message().handle()
async def quick_math(matcher: Matcher, event: GroupMessageEvent):
    global group, answer, group_unanswered
    try:
        if group_unanswered[event.group_id] >= 2:
            group_unanswered[event.group_id] = int(random.choice("0111122222"))
    except BaseException:
        pass
    try:
        if event.group_id == group and answer is not None:
            try:
                _answ = event.get_plaintext().strip().replace("x=", "")
            except ValueError:
                await matcher.finish()
            answer = str(answer)
            if test_regex(answer, _answ) or _answ == str(answer) or\
                    ("/" not in str(_answ) and "regex>" not in str(answer) and
                        run_sandbox(_answ) == run_sandbox(str(answer))):
                group_unanswered[event.group_id] = 0
                add = [random.randint(1, 13), random.randint(1, 15)]
                economy.add_vi(event.get_user_id(), add[0])
                exp.add_exp(event.get_user_id(), add[1])
                await matcher.send(lang.text("quick_math.rightanswer", add, event.get_user_id()),
                                   at_sender=True)
                data = json.load(
                    open("data/quick_math.average.json", encoding="utf-8"))
                data["average"] = round(
                    (data["average"] + (time.time() - send_time)) / 2, 3)
                json.dump(data, open(
                    "data/quick_math.average.json", "w", encoding="utf-8"))
                group = None
                answer = None
                achievement.increase_unlock_progress(
                    "我爱数学", event.get_user_id())
    except BaseException:
        error = format_exc()
        if "LuaError" not in error:
            await error.report(error)


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
