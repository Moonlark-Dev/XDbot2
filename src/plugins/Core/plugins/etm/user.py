from . import data as _data
from .._utils import *
from .._messenger import send_message
from .health import get_max_hp
# from .duel.entity import user

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


def get_hp(user_id: int) -> int:
    if (user_data := get_user_data(user_id))["health"] >= (
        max_hp := get_max_hp(user_id)
    ):
        user_data["health"] = max_hp
        change_user_data(user_id, user_data)
    return user_data["health"]


def remove_hp(user_id: int, count: int) -> None:
    user_data = get_user_data(user_id)
    user_data["health"] -= count
    if user_data["health"] <= 0:
        origin_vimcoin = user_data["vimcoin"]
        user_data["vimcoin"] *= 0.5 if user_data["vimcoin"] > 0 else 1.5
        send_message(
            lang.text(
                "etm_user.died",
                [reduced_vimcoin := origin_vimcoin - user_data["vimcoin"]],
                user_id,
            ),
            str(user_id),
        )
        user_data["health"] = get_max_hp(user_id)
        Json("droped_vimcoin.json")["count"] = (
            Json("droped_vimcoin.json").get("count", 0) + reduced_vimcoin
        )
    change_user_data(user_id, user_data)


# user.get_hp = get_hp
