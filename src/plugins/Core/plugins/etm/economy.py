from . import user
from nonebot_plugin_apscheduler import scheduler
from nonebot import require
import json

vimcoin = json.load(open("data/etm/vimcoin.json"))
#{
#    "in": 0,
#    "out": 0,
#    "exchange_rate": 1
#}
require("nonebot_plugin_apscheduler")

@scheduler.scheduled_job("cron", minute="*/1", id="chamgeExchangeRate")
async def change_exchange_rate():
    vimcoin["exchange_rate"] += vimcoin["exchange_rate"] * (vimcoin["out"] - vimcoin["in"]) / 1000
    vimcoin["in"] = 0
    vimcoin["out"] = 0
    json.dump(vimcoin, open("data/etm/vimcoin.json", "w"))

def add_vimcoin(user_id, count):
    data = user.get_user_data(user_id)
    data["vimcoin"] += count
    user.change_user_data(user_id, data)
    vimcoin["in"] += count

def use_vimcoin(user_id, count):
    data = user.get_user_data(user_id)
    if data["vimcoin"] >= count:
        data["vimcoin"] -= count
        vimcoin["out"] += count
        user.change_user_data(user_id, data)
        return True
    else:
        return False

def vi2vim(vi):
    return round(vi / vimcoin["exchange_rate"], 3)
    
def add_vi(user_id, count):
    add_vimcoin(user_id, vi2vim(count))

def use_vi(user_id, vi):
    used = vi2vim(vi)
    return use_vimcoin(user_id, used), used
