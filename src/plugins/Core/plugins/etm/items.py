from .dice import Dice
from .book_and_quill import BookAndQuill

ITEMS = {
    "dice": Dice,
    "book_and_quill": BookAndQuill
}


def json2items(items, user_id=None):
    item_list = []
    for item in items:
        item_list.append((
            ITEMS[item["id"]](item["count"], item["data"], user_id)
        ))
    return item_list
