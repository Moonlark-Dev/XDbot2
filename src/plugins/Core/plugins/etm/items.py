from . import mystery_box
from .item import Item
from .item_list import ITEMS
from . import rubbish



def json2items(items, user_id=None) -> list[Item]:
    item_list = []
    for item in items:
        item_list.append((ITEMS[item["id"]](item["count"], item["data"], user_id)))
    return item_list

rubbish.json2items = json2items
mystery_box.json2items = json2items
