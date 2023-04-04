from . import user
# from nonebot_plugin_apscheduler import scheduler
from nonebot import require
import json
# from nonebot.log import logger
from .data import vimcoin


# {
#    "in": 0,
#    "out": 0,
#    "exchange_rate": 1
# }
# require("nonebot_plugin_apscheduler")


class IllegalQuantityException(Exception):
    pass


# @scheduler.scheduled_job("cron", hour="*/1", id="additem")
async def add_item():
    vimcoin["item_count"] += 175

vimcoin["exchange_rate"] = 1

# @scheduler.scheduled_job("cron", second="*/15", id="chamgeExchangeRate")

"""
async def change_exchange_rate():
    # 总vi
    users = json.load(open("data/etm/users.json", encoding="utf-8"))
    all_vim = 0
    for user in list(users.values()):
        all_vim += user["vimcoin"]
    all_vi = all_vim * vimcoin["exchange_rate"]
    user_count = len(list(users.keys()))
    vimcoin["_exchange_rate"] += ((vimcoin["item_count"] /
                                  (all_vi / (user_count))) - 1) / 1000
    vimcoin["exchange_rate"] = vimcoin["_exchange_rate"] + 0.25
    json.dump(vimcoin, open("data/etm/vim.json", "w", encoding="utf-8"))
"""


def _add_vimcoin(user_id, count):
    data = user.get_user_data(user_id)
    data["vimcoin"] += count
    user.change_user_data(user_id, data)
    vimcoin["in"] += count


def add_vimcoin(user_id, count):
    if count >= 0:
        _add_vimcoin(user_id, count)
    else:
        raise IllegalQuantityException(count)


def _use_vimcoin(user_id, count):
    data = user.get_user_data(user_id)
    if data["vimcoin"] >= count:
        data["vimcoin"] -= count
        vimcoin["out"] += count
        user.change_user_data(user_id, data)
        return True
    else:
        return False


def use_vimcoin(user_id, count):
    if count >= 0:
        return _use_vimcoin(user_id, count)
    else:
        raise IllegalQuantityException(count)


def vi2vim(vi):
    return round(vi / vimcoin["exchange_rate"], 3)


def _add_vi(user_id, count):
    _add_vimcoin(user_id, vi2vim(count))


def add_vi(user_id, count):
    add_vimcoin(user_id, vi2vim(count))


def remove_vi(user_id, count):
    _use_vimcoin(user_id, count)


def use_vi(user_id, vi):
    used = vi2vim(vi)
    return use_vimcoin(user_id, used), used
