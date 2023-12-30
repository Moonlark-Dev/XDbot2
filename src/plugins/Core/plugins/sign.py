import asyncio
from nonebot import on_command, on_regex
from . import _error as error
from nonebot.adapters.onebot.v11.event import MessageEvent
from . import _lang as lang
from .etm import economy, exp, user, achievement, buff
import traceback
import random
import time
import json
from .email import send_email

from decimal import Decimal

sign = on_regex("^(签到|.sign)$")
sign_rank = on_command("sign-rank")


async def create_returning_gift(user_id: str) -> None:
    """
    发放回归礼物 (#498)

    Args:
        user_id (str): 用户 ID
    """
    await send_email(
        user_id,
        lang.text("sign.returning_email_subject", [], user_id),
        lang.text("sign.returning_email_message", [], user_id),
        [{"id": "vimcoin", "count": 500, "data": {}}],
    )


def _sign(qq) -> str:
    """用户签到

    Args:
        qq (str): 操作目标QQ

    Returns:
        str: 显示的文本
    """
    data = json.load(open("data/etm/sign.json", encoding="utf-8"))
    date = int((time.time() + 28800) / 86400)
    if qq not in data["latest"]:
        data["latest"][qq] = 0
        data["days"][qq] = 0
    origin_data = user.get_user_data(qq)
    if data["latest"][qq] != date:
        add_vi, add_exp = random.randint(0, 20), random.randint(0, 20)
        if data["latest"][qq] == (date - 1):
            data["days"][qq] += 1
        elif date - data["latest"][qq] >= 30:
            asyncio.create_task(create_returning_gift(qq))
            data["days"][qq] = 1
        else:
            data["days"][qq] = 1
        add_vi *= 1 + min(data["days"][qq], 15) / Decimal(20)
        add_exp *= 1 + min(data["days"][qq], 15) / Decimal(20)
        add_vi *= 1 + exp.get_user_level(qq) / Decimal(75)
        add_exp *= 1 + exp.get_user_level(qq) / Decimal(50)
        add_vi /= Decimal("1.2")
        add_vi = round(add_vi, 3)
        add_exp = round(add_exp, 0)
        exp.add_exp(qq, float(add_exp))
        economy.add_vi(qq, int(add_vi))
        data["latest"][qq] = date
        now_data = user.get_user_data(qq)
        json.dump(data, open("data/etm/sign.json", "w", encoding="utf-8"))
        if add_vi == Decimal(0):
            achievement.unlock("+0！", qq)
        if exp.get_user_level(qq) >= 30:
            buff.add_buff(
                qq,
                "每日GPT限免",
                duration=(int(time.time() / 86400) + 1) * 86400 - time.time(),
            )

        return "\n".join(
            [
                lang.text("sign.success", [], qq),
                lang.text("sign.hr", [], qq),
                lang.text(
                    "sign.add_exp",
                    [round(origin_data["exp"], 2), round(now_data["exp"], 2), add_exp],
                    qq,
                ),
                lang.text(
                    "sign.add_vim",
                    [
                        round(origin_data["vimcoin"], 2),
                        round(now_data["vimcoin"], 2),
                        add_vi,
                    ],
                    qq,
                ),
                lang.text("sign.hr", [], qq),
                lang.text("sign.days", [data["days"][qq]], qq),
            ]
        )
    else:
        return "主人今天已经签到过了喵！"


@sign.handle()
async def sign_handler(event: MessageEvent):
    try:
        await sign.finish(_sign(event.get_user_id()))
    except BaseException:
        await error.report(traceback.format_exc(), sign)
