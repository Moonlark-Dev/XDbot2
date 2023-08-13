import os
import os.path
import json
from nonebot import require
from nonebot import get_driver
from nonebot_plugin_apscheduler import scheduler

achi_user_data = {}
achi_unlock_progress = {}
bags = {}
buff = {}
vimcoin = {"in": 0, "out": 0, "exchange_rate": 1, "_exchange_rate": 1}
bank_lead_data = {}
basic_data = {}
emails = {}
require("nonebot_plugin_apscheduler")


def load_data():
    users = os.listdir("data/etm")
    for user in users:
        if os.path.isdir(os.path.join("data", "etm", user)):
            try:
                achi_user_data[user] = json.load(
                    open(f"data/etm/{user}/achi.json", encoding="utf-8"))

            except BaseException:
                pass
            try:
                achi_unlock_progress[user] = json.load(
                    open(f"data/etm/{user}/achi_unlock_progress.json",
                         encoding="utf-8"))
            except BaseException:
                pass
            try:
                bags[user] = json.load(
                    open(f"data/etm/{user}/bag.json", encoding="utf-8"))
            except BaseException:
                pass
            try:
                basic_data[user] = json.load(
                    open(f"data/etm/{user}/user.json", encoding="utf-8"))
            except BaseException:
                pass
            try:
                buff[user] = json.load(
                    open(f"data/etm/{user}/buff.json", encoding="utf-8"))
            except BaseException:
                pass
            try:
                bank_lead_data[user] = json.load(
                    open(f"data/etm/{user}/bank_lead_data.json",
                         encoding="utf-8"))
            except BaseException:
                pass
            try:
                emails[user] = json.load(
                    open(f"data/etm/{user}/emails.json", encoding="utf-8"))
            except BaseException:
                pass


load_data()


def _save_data(name, data):
    users = list(data.keys())
    for user in users:
        if not os.path.isdir(f"data/etm/{user}"):
            os.mkdir(f"data/etm/{user}")
        json.dump(data[user],
                  open(f"data/etm/{user}/{name}.json", "w", encoding="utf-8"))


def save_data():
    _save_data("achi", achi_user_data)
    _save_data("achi_unlock_progress", achi_unlock_progress)
    _save_data("bag", bags)
    _save_data("user", basic_data)
    _save_data("buff", buff)
    _save_data("bank_lead_data", bank_lead_data)
    _save_data("emails", emails)


@get_driver().on_shutdown
@scheduler.scheduled_job("cron", second="*/20", id="save_data")
async def _():
    save_data()
    load_data()
