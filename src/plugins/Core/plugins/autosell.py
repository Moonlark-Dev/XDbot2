from nonebot_plugin_apscheduler import scheduler
from nonebot import require
import json
import asyncio
import time
# import threading

latestReload = json.load(open("data/autosell.latest.json", encoding="utf-8"))


async def reloadSell():
    # print(114514)
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
                        "nickname": "X-D-B-O-T",
                        "user_id": "1747433912"
                    }
                }
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


"""
@scheduler.scheduled_job("cron", minute="*/1", id="awa")
async def run_every_2_hour():
    await reloadSell()
"""

scheduler.add_job(reloadSell, "interval", days=1, id="reloadAutoSellItems")


# asyncio.create_task(reloadSell())
#threading.Thread(None, reloadSell).start()
