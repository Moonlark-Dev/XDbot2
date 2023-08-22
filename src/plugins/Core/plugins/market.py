import math
import json
from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, Message, MessageEvent, GroupMessageEvent
from nonebot.adapters.onebot.v11.bot import Bot
from nonebot.params import CommandArg
from .etm import items, user, economy, bag, item
from . import _error, _lang
import traceback

market = on_command("market")
data = json.load(open("data/market.items.json", encoding="utf-8"))
average_price = json.load(open("data/market.average.json", encoding="utf-8"))

# [HELPSTART] Version: 2
# Command: market
# Msg: 全球市场
# Info: 全球垃圾场（划掉）市场
# Usage: market list <页码>：查看商品列表
# Usage: market sell <背包物品ID> <卖出总数> <单价>：卖出商品
# Usage: market view <商品ID>：查看商品
# Usage: market buy <商品ID> [数量]：购买商品
# [HELPEND]


def get_average(item_id):
    try:
        return average_price[item_id]
    except BaseException:
        return items.json2items([{"id": item_id, "count": 1, "data": {}}])[0].data[
            "price"
        ]


def save_data():
    json.dump(data, open("data/market.items.json", "w", encoding="utf-8"))
    json.dump(average_price, open("data/market.average.json", "w", encoding="utf-8"))


@market.handle()
async def item_list(
    bot: Bot, event: GroupMessageEvent, message: Message = CommandArg()
):
    try:
        user_id = event.get_user_id()
        argv = str(message).split(" ")
        if argv[0] in ["", "list"]:
            # for id, item_json in list(data.items()):
            # item = items.json2items([item_json["item"]])[0]
            # reply += _lang.text("market.list_item", [
            # id, item.data["display_name"], item_json["price"]], user_id)
            # await market.finish(reply)
            try:
                page = int(argv[1])
            except:
                page = 1
            node_messages = [
                {
                    "type": "node",
                    "data": {
                        "uin": event.self_id,
                        "nickname": "XDBOT2",
                        "content": _lang.text(
                            "market.list_title",
                            [page, math.ceil(len(list(data.items())) / 100)],
                            user_id,
                        ),
                    },
                }
            ]
            for item_data in list(data.values())[page * 100 - 100 : page * 100]:
                item = items.json2items([item_data["item"]])[0]
                node_messages.append(
                    {
                        "type": "node",
                        "data": {
                            "uin": event.self_id,
                            "nickname": "XDBOT2",
                            "content": _lang.text(
                                "market.view",
                                [
                                    item_data["id"],
                                    item.data["display_name"],
                                    item.item_id,
                                    item_data["price"],
                                    min(
                                        int(
                                            user.get_user_data(user_id)["vimcoin"]
                                            / max(1, item_data["price"])
                                        ),
                                        item_data["count"],
                                    ),
                                    item_data["count"],
                                    item_data["seller"]["nickname"],
                                    item_data["seller"]["user_id"],
                                    item.data["display_message"],
                                ],
                                user_id,
                            ),
                        },
                    }
                )
            await bot.call_api(
                "send_group_forward_msg",
                messages=node_messages,
                group_id=event.group_id,
            )
            await market.finish()
    except BaseException:
        await _error.report(traceback.format_exc(), market)


@market.handle()
async def view_item(event: MessageEvent, message: Message = CommandArg()):
    try:
        user_id = event.get_user_id()
        argv = str(message).split(" ")
        if argv[0] == "view":
            item_data = data[argv[1]]
            item = items.json2items([item_data["item"]])[0]
            await market.finish(
                _lang.text(
                    "market.view",
                    [
                        item_data["id"],
                        item.data["display_name"],
                        item.item_id,
                        item_data["price"],
                        min(
                            int(
                                user.get_user_data(user_id)["vimcoin"]
                                / max(1, item_data["price"])
                            ),
                            item_data["count"],
                        ),
                        item_data["count"],
                        item_data["seller"]["nickname"],
                        item_data["seller"]["user_id"],
                        item.data["display_message"],
                    ],
                    user_id,
                )
            )
    except BaseException:
        await _error.report(traceback.format_exc(), market)


def check_item(item: item.Item, keyword: str):
    return (
        keyword == item.item_id
        or keyword in item.data["display_message"]
        or keyword in item.data["display_name"]
    )


@market.handle()
async def search_item(
    bot: Bot, event: GroupMessageEvent, message: Message = CommandArg()
):
    try:
        user_id = event.get_user_id()
        argv = str(message).split(" ")
        if argv[0] in ["search", "搜索"]:
            node_messages = [
                {
                    "type": "node",
                    "data": {
                        "uin": event.self_id,
                        "nickname": "XDBOT2",
                        "content": _lang.text(
                            "market.search_title", [argv[1]], user_id
                        ),
                    },
                }
            ]
            item_count = 0
            for item_data in list(data.values()):
                item = items.json2items([item_data["item"]])[0]
                if not check_item(item, argv[1]):
                    continue
                item_count += 1
                node_messages.append(
                    {
                        "type": "node",
                        "data": {
                            "uin": event.self_id,
                            "nickname": "XDBOT2",
                            "content": _lang.text(
                                "market.view",
                                [
                                    item_data["id"],
                                    item.data["display_name"],
                                    item.item_id,
                                    item_data["price"],
                                    min(
                                        int(
                                            user.get_user_data(user_id)["vimcoin"]
                                            / max(1, item_data["price"])
                                        ),
                                        item_data["count"],
                                    ),
                                    item_data["count"],
                                    item_data["seller"]["nickname"],
                                    item_data["seller"]["user_id"],
                                    item.data["display_message"],
                                ],
                                user_id,
                            ),
                        },
                    }
                )
                if item_count >= 100:
                    break
            await bot.call_api(
                "send_group_forward_msg",
                messages=node_messages,
                group_id=event.group_id,
            )
            await market.finish()

    except:
        await _error.report()


@market.handle()
async def buy_item(event: MessageEvent, message: Message = CommandArg()):
    try:
        user_id = event.get_user_id()
        argv = str(message).split(" ")
        if argv[0] == "buy":
            item_json = data[argv[1]]
            try:
                count = max(int(argv[2]), 1)
            except BaseException:
                count = 1
            if count <= item_json["count"]:
                if economy.use_vimcoin(user_id, count * item_json["price"]):
                    bag.add_item(
                        user_id,
                        item_json["item"]["id"],
                        count,
                        item_json["item"]["data"],
                    )
                    economy.add_vimcoin(user_id, count * item_json["price"])
                    try:
                        average_price[item_json["item"]["id"]] = (
                            average_price[item_json["item"]["id"]]
                            + count * item_json["price"]
                        ) / count + 1
                    except BaseException:
                        average_price[item_json["item"]["id"]] = item_json["price"]
                    save_data()
                    data[argv[1]]["count"] -= count
                    save_data()
                    if data[argv[1]]["count"] == 0:
                        data.pop(argv[1])
                    await market.finish("购买成功！")
                else:
                    await market.finish("错误：余额不足！")
            else:
                await market.finish("错误：库存不足")
    except BaseException:
        await _error.report(traceback.format_exc(), market)


@market.handle()
async def sell_item(event: MessageEvent, bot: Bot, message: Message = CommandArg()):
    try:
        user_id = event.get_user_id()
        argv = str(message).split(" ")
        if argv[0] == "sell":
            item = bag.get_user_bag(user_id)[int(argv[1]) - 1]
            count = max(1, int(argv[2]))
            price = max(0, float(argv[3]))
            if item.data["can_be_sold"]:
                if count <= item.count:
                    if (
                        price
                        <= min(get_average(item.item_id) * 2, item.data["price"] * 7)
                        or item.item_id == "pouch"
                    ):
                        id = 1
                        while True:
                            if str(id) not in data.keys():
                                break
                            else:
                                id += 1
                        data[str(id)] = {
                            "id": str(id),
                            "count": count,
                            "item": {"id": item.item_id, "count": 1, "data": item.data},
                            "seller": await bot.get_stranger_info(user_id=user_id),
                            "price": price,
                        }
                        save_data()
                        item.count -= count
                        await market.finish(f"已出售（#{id}）")
                    else:
                        await market.finish("失败：价格过高")
                else:
                    await market.finish("失败：数量不足")
            else:
                await market.finish("失败：物品不可出售")

    except BaseException:
        await _error.report(traceback.format_exc(), market)
