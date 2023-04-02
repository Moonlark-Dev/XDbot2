from nonebot import on_command, on_fullmatch
from . import _error as error
from nonebot.adapters.onebot.v11.event import MessageEvent
from . import _lang as lang
from .etm import economy, exp, user, achievement
import traceback
import random
import time
import json

from decimal import Decimal

sign = on_fullmatch(("签到", ".sign"))
sign_rank = on_command("sign-rank")


@sign.handle()
async def sign_handler(event: MessageEvent):
    try:
        data = json.load(open("data/etm/sign.json", encoding="utf-8"))
        qq = event.get_user_id()
        date = int((time.time() + 28800) / 86400)
        if qq not in data["latest"]:
            data["latest"][qq] = 0
            data["days"][qq] = 0
        origin_data = user.get_user_data(qq)

        if data["latest"][qq] != date:
            add_vi, add_exp = random.randint(0, 20), random.randint(0, 20)
            if data["latest"][qq] == (date - 1):
                data["days"][qq] += 1
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
            await sign.send("\n".join((
                lang.text("sign.success", [], qq),
                lang.text("sign.hr", [], qq),
                lang.text(
                    "sign.add_exp", [
                        round(origin_data["exp"], 2), round(now_data["exp"], 2), add_exp], qq),
                lang.text(
                    "sign.add_vim", [
                        round(origin_data["vimcoin"], 2), round(now_data["vimcoin"], 2), add_vi], qq),
                lang.text("sign.hr", [], qq),
                lang.text("sign.days", [data["days"][qq]], qq)
            )), at_sender=True)
            json.dump(data, open("data/etm/sign.json", "w", encoding="utf-8"))
            if add_vi == Decimal(0):
                achievement.unlck("+0！", event.get_user_id())

    except BaseException:
        await error.report(traceback.format_exc(), sign)
