# from .item_list import ITEMS
# from .duel.entity import user
from typing import Type

from .items.unknown_item import UnknownItem
from .item import Item

# from . import get_items
# from .items import (
#     mystery_box,
#     rubbish,
#     pouch
# )

ITEMS = {}


def setup_items(item_list: dict[str, Type[Item]]) -> None:
    global ITEMS
    ITEMS = item_list


def json2items(items: list[dict], user_id=None) -> list[Item]:
    item_list = []
    for item in items:
        try:
            item_list.append((ITEMS[item["id"]](item["count"], item["data"], user_id)))
        except KeyError:
            item_list.append(UnknownItem(item["count"], item["data"], user_id))
    return item_list
