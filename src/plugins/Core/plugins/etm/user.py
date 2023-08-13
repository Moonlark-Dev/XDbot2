from . import data as _data

RAW_DATA = {"user_id": None, "exp": 0, "health": 20, "vimcoin": 0}


def get_user_data(user_id):
    try:
        return _data.basic_data[user_id].copy()
    except KeyError:
        data = RAW_DATA.copy()
        data["user_id"] = user_id
        return data


def change_user_data(user_id, data):
    _data.basic_data[user_id] = data
