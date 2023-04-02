import json

RAW_DATA = {"user_id": None, "exp": 0, "health": 20, "vimcoin": 0}


def get_user_data(user_id):
    try:
        return json.load(open("data/etm/users.json", encoding="utf-8"))[user_id]
    except KeyError:
        data = RAW_DATA
        data["user_id"] = user_id
        return data


def change_user_data(user_id, data):
    origin = json.load(open("data/etm/users.json", encoding="utf-8"))
    origin[user_id] = data
    json.dump(origin, open("data/etm/users.json", "w", encoding="utf-8"))
