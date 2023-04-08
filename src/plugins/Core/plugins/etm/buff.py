from time import time
from . import data

BUFFERS = {
    "护符": {
        "max_effect": lambda _: 5,
        "default_level": None
    }
}

def get_buff_level(user_id, buff_id):
    try:
        buff = data.buff[user_id]
        if buff["endtime"] != None:
            if time() > buff["endtime"]:
                data.buff[user_id].pop(buff_id)
                return BUFFERS[buff_id]["default_level"]
        return data.buff[user_id][buff_id]["level"]
    except:
        return BUFFERS[buff_id]["default_level"]

def effect_buff(user_id, buff_id):
    try:
        data.buff[user_id][buff_id]["effect_count"] += 1
        if data.buff[user_id][buff_id]["effect_count"] >= BUFFERS[buff_id]["max_effect"](data.buff[user_id][buff_id]["level"]):
            data.buff[user_id].pop(buff_id)
        return True
    except:
        return False

def can_effect(user_id, buff_id):
    try:
        if data.buff[user_id][buff_id]["effect_count"] >= BUFFERS[buff_id]["max_effect"](data.buff[user_id][buff_id]["level"]):
            return False
        return True
    except:
        return False

def give_buff(user_id, buff_id, buff_level, endtime = None, effect_count = 0):
    if user_id not in data.buff.keys():
        data.buff[user_id] = {}
    data.buff[user_id][buff_id] = {
        "level": buff_level,
        "endtime": endtime,
        "effect_count": effect_count
    }
    data.save_data()

