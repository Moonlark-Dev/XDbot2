import time
from ._utils import *
from .etm.json2items import json2items
from .etm import bag
from .etm.bag import overflow


def view_item(user_id: str, item_id: str) -> str:
    item_data = overflow.get_overflow(user_id).get(item_id)
    if item_data is None:
        return lang.text("bag_overflow.not_found", [item_id], user_id)
    item = json2items([item_data], user_id)[0]
    return lang.text(
        "bag_overflow.item",
        [
            item.data["display_name"],
            item.item_id,
            item.count,
            time.strftime("%H:%M:%S", time.localtime(time.time() - item_data["time"])),
            item.data["display_message"],
        ],
        user_id,
    )


def get_item(user_id: str, item_id: str) -> str:
    item = overflow.get_overflow(user_id).get(item_id)
    if item is None:
        return lang.text("bag_overflow.not_found", [item_id], user_id)
    bag.add_item(user_id, item["id"], item["count"], item["data"])
    return lang.text(get_currency_key("ok"), [], user_id)


@create_command("bag-overflow")
async def _(bot: Bot, event: MessageEvent, message: Message):
    argv = message.extract_plain_text().split(" ")
    user_id = event.get_user_id()
    match argv[0]:
        case "get":
            try:
                await finish(
                    get_currency_key("empty"), [get_item(user_id, argv[1])], user_id
                )
            except IndexError:
                for key in overflow.get_overflow(user_id).keys():
                    get_item(user_id, key)
                await finish(get_currency_key("ok"), [], user_id)

        case "view":
            await finish(
                get_currency_key("empty"), [view_item(user_id, argv[1])], user_id
            )

        case _:
            await send_node_message(
                bot,
                await generate_node_message(
                    bot,
                    [
                        view_item(user_id, item_id)
                        for item_id in overflow.get_overflow(user_id).keys()
                    ],
                ),
                event,
            )


# [HELPSTART] Version: 2
# Command: bag-overflow
# Usage: bag-overflow：获取溢出物品列表
# Usage: bag-overflow view <ID>：查看物品详情
# Usage: bag-overflow get [ID]：取走物品
# Msg: 溢出物品
# Info: 背包溢出物品区域
# [HELPEND]
