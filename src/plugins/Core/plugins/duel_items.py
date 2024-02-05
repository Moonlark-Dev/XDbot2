from ._utils import *
from .etm.json2items import json2items
from .etm.duel.item import DuelItem

# [HELPSTART] Version: 2
# Command: duel-items
# Usage: duel-items
# Msg: 查看装备
# Info: 查看装备
# [HELPEND]


def get_items(user_id: int) -> list[DuelItem]:
    item_list = []
    for item_data in Json(f"duel2/users/{user_id}.json").get("items", {}).values():
        if isinstance(item_data, dict):
            items = [item_data]
        else:
            items = item_data
        item_list += [
            i for i in json2items(items, str(user_id)) if isinstance(i, DuelItem)
        ]
    return item_list


def get_item_list(user_id: int) -> str:
    length = 0
    text = ""
    for item in get_items(user_id):
        length += 1
        text += lang.text(
            "duel_items.list_item",
            [
                lang.text(f"duel_items.type_{item.DUEL_ITEM_TYPE}", [], user_id),
                length,
                item.data["display_name"],
                item.count,
            ],
            user_id,
        )
    return text


@create_command("duel-items", {"duel-item", "duel-i"})
async def _(bot: Bot, event: MessageEvent, message: Message) -> None:
    # argv = message.extract_plain_text().split(" ")
    await finish(
        "duel_items.list", [get_item_list(event.user_id)], event.user_id, False, True
    )
