import hashlib
import json
import os
import time
from .account import multiAccountData
from .etm import data
from nonebot import get_bot, get_bots


async def submit_email(mail_data):
    users = os.listdir("data/etm")
    # 收集数据
    _user = []
    for rule in mail_data["rules"]:
        if rule[0] == "group":
            try:
                bot = get_bot(multiAccountData[rule[1]])
            except BaseException:
                bot = list(get_bots().values())[0]
            group_member_list = await bot.get_group_member_list(group_id=rule[1])
            for user in group_member_list:
                _user.append(str(user["user_id"]))
                # print(_user)

    # 比对用户
    for user_id in users:
        if os.path.isdir(os.path.join("data", "etm", user_id)):
            user_can_receive = True
            for rule in mail_data["rules"]:
                match rule[0]:
                    case "group":
                        if user_id not in _user:
                            user_can_receive = False
                            break
                    case "user":
                        if user_id != rule[1]:
                            user_can_receive = False
                            break
                    case "bot":
                        pass  # TODO 按Bot筛选用户
            if user_id not in data.emails.keys():
                data.emails[user_id] = []
            if user_can_receive:
                data.emails[user_id].append(mail_data["id"])


async def send_email(
    receive: str, subject: str, message: str, items: list = [], **params
) -> str:
    data = json.load(open("data/su.mails.json", encoding="utf-8"))
    mail_id = hashlib.sha1(str(time.time()).encode("utf-8")).hexdigest()[:7]
    data[mail_id] = {
        "message": message,
        "subject": subject,
        "from": "XDBOT",
        "rules": [["user", receive]],
        "items": items,
        "time": time.time(),
        "id": mail_id,
    }
    data[mail_id].update(params)
    json.dump(
        data,
        open("data/su.mails.json", "w", encoding="utf-8"),
        ensure_ascii=False,
        indent=4,
    )
    await submit_email(data[mail_id])
    return mail_id
