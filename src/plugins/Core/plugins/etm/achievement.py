import asyncio
from . import bag
from .. import _lang as lang
from ..send_email import send_email
from . import exp
import json
import time
from . import data
import os.path

ACHIEVEMENTS = json.load(
    open(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "achievement.json"),
        encoding="utf-8",
    )
)


def get_user_achievement(user_id):
    try:
        return data.achi_user_data[user_id]
    except KeyError:
        return []


def change_user_achievement(user_id, _data):
    data.achi_user_data[user_id] = _data


def unlock(name, user_id):
    user_achievement = get_user_achievement(user_id)
    if name in ACHIEVEMENTS.keys() and name not in user_achievement:
        user_achievement.append(name)
        asyncio.create_task(
            send_email(
                str(user_id),
                lang.text("achievement.email_title", [name], user_id),
                ACHIEVEMENTS[name]["condition"],
                ACHIEVEMENTS[name]["award"],
            )
        )


def get_unlck_progress(name, user_id):
    user_data = data.achi_unlock_progress
    try:
        return user_data[user_id][name]
    except KeyError:
        return None


def increase_unlock_progress(name, user_id, count=1):
    try:
        data.achi_unlock_progress[user_id][name] += count
    except KeyError:
        try:
            data.achi_unlock_progress[user_id][name] = count
        except KeyError:
            data.achi_unlock_progress[user_id] = {name: count}
    if data.achi_unlock_progress[user_id][name] >= ACHIEVEMENTS[name]["need_progress"]:
        unlock(name, user_id)
