from .dice import Dice

ITEMS = {
    "dice": Dice
}

def json2items(items, user_id = None):
    item_list = []
    for item in items:
        item_list.append((
            ITEMS[item["id"]](item["count"], item["data"], user_id)
        ))
    return item_list
