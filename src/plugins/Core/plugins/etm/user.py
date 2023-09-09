from . import data as _data
from .health import get_max_hp

RAW_DATA = {"user_id": None, "exp": 0, "health": 100, "vimcoin": 0}


def get_user_data(user_id):
    try:
        return _data.basic_data[str(user_id)].copy()
    except KeyError:
        data = RAW_DATA.copy()
        data["user_id"] = str(user_id)
        data["health"] = get_max_hp(user_id)
        return data


def change_user_data(user_id, data):
    _data.basic_data[str(user_id)] = data
