from .._utils import Json
import time
from .bag_crr import add_crr

def add_overflow(user_id: str, item_id: str, item_count: int, item_data: dict) -> None:
    data = Json("etm.overflow.json")
    data.update({user_id: {}})
    _id = 0
    while True:
        if _id not in data[user_id]:
            data[user_id][str(_id)] = {
                "id": item_id,
                "count": item_count,
                "data": item_data,
                "time": time.time()
            }
            break
        _id += 1
    data.changed_key.add(user_id)

def get_overflow(user_id: str):
    check_user_overflow(user_id)
    return Json("etm.overflow.json").get(user_id, {})

def pop_item(user_id: str, _id: str) -> dict:
    data = Json("etm.overflow.json")
    data.changed_key.add(user_id)
    return data[user_id].pop(_id)

def check_overflow_item(user_id: str, _id: str) -> None:
    if time.time() - Json("etm.overflow.json")[user_id][_id]["time"] >= 1800:
        item = pop_item(user_id, _id):
        add_crr(
            item["id"],
            item["count"],
            item["data"]
        )

def check_user_overflow(user_id: str) -> None:
    data = Json("etm.overflow.json")
    data.update({user_id: {}})
    for _id in data[user_id].keys():
        check_overflow_item(user_id, _id)

def check_overflow() -> None:
    for user_id in Json("etm.overflow.json").keys():
        check_user_overflow(user_id)
