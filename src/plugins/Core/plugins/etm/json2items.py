from .items import mystery_box
from .item import Item
from .item_list import ITEMS
from .items import rubbish
from .duel.entity import user


def json2items(items: list[dict], user_id=None) -> list[Item]:
    item_list = []
    for item in items:
        try:
            item_list.append((ITEMS[item["id"]](item["count"], item["data"], user_id)))
        except KeyError:
            pass
    return item_list


rubbish.json2items = json2items
mystery_box.json2items = json2items
user.json2items = json2items