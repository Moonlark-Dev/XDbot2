from io import BytesIO
import time
import json
from ._utils import *
import random
from sympy import Symbol, Eq, solve, latex
from nonebot_plugin_apscheduler import scheduler
from nonebot import get_bot, on_fullmatch, require
from PIL import Image, ImageDraw, ImageFont
from nonebot.adapters.onebot.v11.message import MessageSegment
import asyncio


require("nonebot_plugin_apscheduler")
eggs = {
    "0/0=?": "regex>([nN][aA][nN])|(0)",
    "1/0=?": "regex>[iI][nN][fF]",
    "creeper?": "regex>[aA][wW]+.*?[mM][aA][N](.*?)",
    "undefined+undefined=?": "regex>[nN][aA][nN]|[uU][nN][dD][fF][iI][nN][eE][dD]",
    "114+514=?": "regex>哼+啊+|114|514|114514|1919|810|1919810",
}


def render_question(question_string: str) -> bytes:
    title_font = ImageFont.truetype("./src/plugins/Core/font/HYRunYuan-55W.ttf", 17)
    question_font = ImageFont.truetype("./src/plugins/Core/font/HYRunYuan-55W.ttf", 20)
    width1, height1 = question_font.getsize(question_string)  # type: ignore
    width2, height2 = title_font.getsize("[QUICK MATH]")  # type: ignore
    image = Image.new("RGB", (max(width1, width2), 40), color="white")
    draw = ImageDraw.Draw(image)
    draw.text((0, 18), question_string, fill="black", font=question_font)
    draw.text((0, 0), "[QUICK MATH]", fill="black", font=title_font)
    bbox = image.getbbox()
    image = image.crop(bbox)
    io = BytesIO()
    image.save(io, format="PNG")
    return io.getvalue()


def get_group() -> int:
    try:
        return random.choice(
            json.load(open("data/quick_math.enabled_groups.json", encoding="utf-8"))
        )
    except BaseException:
        return 0


def check_group(group_id: int) -> bool:
    return bool(
        group_id and Json("quickmath/group_unanswered.json").get(str(group_id), 0) <= 3
    )


def generate_question():
    if random.random() <= 0.5:
        question = (
            f"{random.randint(0, 50)}{random.choice('+-*')}{random.randint(1, 50)}"
        )
        answer = [str(tmp := eval(question))]
        question += "=?"
    else:
        x = Symbol("x")
        a, b = random.randint(1, 10), random.randint(1, 10)
        eq = Eq(a * x + b, random.randint(1, 50))  # type: ignore
        ans = solve(eq)
        question = latex(eq)
        answer = [(tmp := str(ans).replace("[", "").replace("]", "")), str(eval(tmp))]
    return question, answer


@scheduler.scheduled_job("cron", minute="*/2", id="send_quick_math")
async def send_quick_math():
    try:
        if not check_group(group := get_group()):
            return
        question, answer = generate_question()
        bot = get_bot(Json("su.multiaccoutdata.ro.json")[str(group)])
        msg_id = (
            await bot.send_group_msg(
                group_id=group, message=MessageSegment.image(render_question(question))
            )
        )["message_id"]
        matcher = on_fullmatch(tuple(answer))
        send_time = time.time()
        answered = False

        @matcher.handle()
        async def handle_quickmath_answer(event: GroupMessageEvent) -> None:
            nonlocal answered
            try:
                await send_text(
                    "quick_math.rightanswer1",
                    [(add_score := int(2 * (20 - time.time() + send_time)))],
                    event.user_id,
                    False,
                    True,
                )
                matcher.destroy()
                answered = True
                Json(f"etm/{event.user_id}/quickmath.json")["score"] = (
                    Json(f"etm/{event.user_id}/quickmath.json").get("score", 0)
                    + add_score
                )
            except:
                await error.report()

        await asyncio.sleep(20)
        if not answered:
            matcher.destroy()
            await bot.delete_msg(message_id=msg_id)

    except:
        await error.report()
