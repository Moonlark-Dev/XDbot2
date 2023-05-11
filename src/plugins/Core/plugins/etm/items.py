from .dice import Dice
from .talisman import Talisman
from .book_and_quill import BookAndQuill
from .pouch import Pouch

ITEMS = {
    "dice": Dice,
    "book_and_quill": BookAndQuill,
    "talisman": Talisman,
    "pouch": Pouch
}


def json2items(items, user_id=None):
    item_list = []
    for item in items:
        item_list.append((
            ITEMS[item["id"]](item["count"], item["data"], user_id)
        ))
    return item_list
