from time import time
from typing import Optional
from . import data
import json

BUFF_LIST = json.load(open("src/plugins/Core/plugins/etm/buffs.json", encoding="utf-8"))


def refresh_buff():
    for user_id, buffs in list(data.buff.items()):
        for buff in buffs:
            if buff.get("number_of_times_remaining", 114514) <= 0 or time() > buff.get(
                "end_time", time() + 114514
            ):
                data.buff[user_id].pop(data.buff[user_id].index(buff))


#
# def get_buff_level(user_id, buff_id):
#     try:
#         buff = data.buff[user_id]
#         if buff["endtime"] is not None:
#             if time() > buff["endtime"]:
#                 data.buff[user_id].pop(buff_id)
#                 return BUFF_LIST[buff_id]["default_level"]
#         return data.buff[user_id][buff_id]["level"]
#     except BaseException:
#         return BUFF_LIST[buff_id]["default_level"]


def effect_buff(user_id: str, buff_id: str) -> bool:
    refresh_buff()
    length = 0
    for buff in data.buff[user_id]:
        if buff["buff_id"] == buff_id and "number_of_times_remaining" in buff.keys():
            data.buff[user_id][length]["number_of_times_remaining"] -= 1
            refresh_buff()
            return True
        elif buff["buff_id"] == buff_id:
            return True
        length += 1
    return False


def has_buff(user_id: str, buff_id: str, levels: list = []) -> bool:
    """用户是否拥有Buff

    Args:
        user_id (str): 用户ID
        buff_id (str): 效果ID
        levels (list, optional): 允许的等级，空列表则为全部. Defaults to [].

    Returns:
        bool: 用户是否拥有符合条件的效果
    """
    refresh_buff()
    for buff in data.buff.get(user_id, []):
        if buff["buff_id"] == buff_id:
            if levels and buff["level"] not in levels:
                continue
            return True
    return False


def get_remain_times(user_id: str, buff_id: str, levels: list = []) -> int:
    """获取用户符合条件的效果剩余的生效次数

    Args:
        user_id (str): 用户ID
        buff_id (str): 效果ID
        levels (list, optional): 允许的等级，空列表则为不筛选等级. Defaults to [].

    Returns:
        int: 剩余生效次数
    """
    refresh_buff()
    times = 0
    for buff in data.buff.get(user_id, []):
        if buff["buff_id"] == buff_id:
            if levels and buff["level"] not in levels:
                continue
            times += buff["number_of_times_remaining"]
    return times


def add_buff(
    user_id: str, buff_id: str, buff_level: int = 1, duration: int | None = None
):
    if user_id not in data.buff.keys():
        data.buff[user_id] = []
    buff_data = BUFF_LIST[buff_id].copy()
    buff_data["buff_id"] = buff_id
    for key in list(buff_data.keys()):
        if isinstance(buff_data[key], list):
            buff_data[key] = buff_data[key][buff_level - 1]
    if "max_effect" in buff_data.keys():
        buff_data["number_of_times_remaining"] = buff_data["max_effect"]
    if buff_data["duration"]:
        buff_data["end_time"] = time() + buff_data["duration"]
    if duration:
        buff_data["end_time"] = time() + duration
    data.buff[user_id].append(buff_data)

    data.save_data()


def get_buff(user_id: str, buff_id: str, levels: list = []) -> Optional[dict]:
    refresh_buff()
    for buff in data.buff.get(user_id, []):
        if buff["buff_id"] == buff_id:
            if levels and buff["level"] not in levels:
                continue
            return buff
