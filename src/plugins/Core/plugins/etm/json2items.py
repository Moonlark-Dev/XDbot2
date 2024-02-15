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


class ItemsHelper:
    def __init__(self) -> None:
        self.items = {}
        # print("1"*30)


item_helper = ItemsHelper()


def json2items(items: list[dict], user_id=None) -> list[Item]:
    # print(item_helper.items)
    item_list = []
    for item in items:
        try:
            item_list.append(
                (item_helper.items[item["id"]](item["count"], item["data"], user_id))
            )
        except KeyError:
            item_list.append(UnknownItem(item["count"], item["data"], user_id))
    return item_list
