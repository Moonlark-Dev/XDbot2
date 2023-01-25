import json
import time

from nonebot import require
from nonebot.log import logger
from nonebot_plugin_apscheduler import scheduler

# import threading

latestReload = json.load(open("data/autosell.latest.json", encoding="utf-8"))


async def reloadSell():
    shopData = json.load(
        open(
            "data/shop.items.json",
            encoding="utf-8"))
    # 删除原来的
    temp0 = shopData.keys()
    for item in list(temp0):
        if "from" in shopData[item]:
            if shopData[item]["from"] == "autosell":
                shopData.pop(item)
    # 加上新的
    sellData = json.load(
        open(
            "data/autosell.items.json",
            encoding="utf-8"))
    items = json.load(open("data/etm.items.json", encoding="utf-8"))
    for item in sellData:
        length = 0
        while True:
            if str(length) not in shopData.keys():
                try:
                    s_nickname = item["nickname"]
                    s_user_id = item["user_id"]
                except KeyError:
                    s_nickname = "System"
                    s_user_id = "AdminShop"
                shopData[str(length)] = {
                    "name": items[item["id"]]["name"],
                    "info": items[item["id"]]["info"],
                    "item": {
                        "id": item["id"],
                        "count": 1,
                        "data": item["data"]
                    },
                    "count": item["count"],
                    "price": item["price"],
                    "from": "autosell",
                    "seller": {
                        "nickname": s_nickname,
                        "user_id": s_user_id,
                    }
                }
                try:
                    shopData[str(length)]["maxBuy"] = int(item["maxBuy"])
                except KeyError:
                    pass
                break
            length += 1
        json.dump(
            shopData,
            open(
                "data/shop.items.json",
                "w",
                encoding="utf-8"))
# await asyncio.sleep(60)


require("nonebot_plugin_apscheduler")


@scheduler.scheduled_job("cron", minute="*/2", id="reloadSell")
async def checkReloaded():
    latest = json.load(open("data/autosell.latest.json", encoding="utf-8"))
    if latest["mday"] != time.localtime().tm_mday:
        logger.info("正在刷新商城货架")
        try:
            await reloadSell()
        except BaseException as e:
            logger.error(e)
        else:
            latest["mday"] = time.localtime().tm_mday
            json.dump(
                latest,
                open(
                    "data/autosell.latest.json",
                    "w",
                    encoding="utf-8"))
