from . import user
from nonebot_plugin_apscheduler import scheduler
from nonebot import require
import json
from nonebot.log import logger

vimcoin = json.load(open("data/etm/vimcoin.json", encoding="utf-8"))
#{
#    "in": 0,
#    "out": 0,
#    "exchange_rate": 1
#}
require("nonebot_plugin_apscheduler")
class IllegalQuantityException(Exception): pass

@scheduler.scheduled_job("cron", second="*/15", id="chamgeExchangeRate")
async def change_exchange_rate():
    # 一阶段
    exchange_rate = vimcoin["exchange_rate"]
    vimcoin["exchange_rate"] += (vimcoin["out"] - vimcoin["in"]) / 250
    vimcoin["in"] = 0
    vimcoin["out"] = 0
    if vimcoin["exchange_rate"] <= 0:
        vimcoin["exchange_rate"] = exchange_rate
        logger.error("更新汇率失败：非法数据（已放弃）")
    # 二阶段
    data = json.load(open("data/etm/users.json", encoding="utf-8"))
    all_vimcoin = 0
    for user in list(data.values()):
        all_vimcoin += user["vimcoin"]
    all_vi = all_vimcoin * vimcoin["exchange_rate"]
    temp = all_vi / len(list(data.keys()))
    vi = 500
    print(all_vi, temp, vi)
    vimcoin["exchange_rate"] = vimcoin["exchange_rate"] / (temp - vi) / 25 + 1
    vimcoin["exchange_rate"] = exchange_rate * vimcoin["exchange_rate"]
    json.dump(vimcoin, open("data/etm/vimcoin.json", "w", encoding="utf-8"))

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
