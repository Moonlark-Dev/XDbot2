from ..._utils import Json


def add_crr(item_id: str, item_count: int, item_data: dict) -> None:
    data = Json("etm.crr.json")
    _id = 0
    while True:
        if _id not in data.keys():
            data[str(_id)] = {"id": item_id, "count": item_count, "data": item_data}
            break
        _id += 1


def pop_item(_id: str) -> dict:
    data = Json("etm.crr.json")
    return data.pop(_id)
