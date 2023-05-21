from .etm import items, data
from .su import su
from .userinfo import panel
from .sign import sign
import os
from nonebot import on_command, get_bot, get_bots
from nonebot.matcher import Matcher
from nonebot.adapters.onebot.v11 import MessageEvent
from nonebot.adapters.onebot.v11 import Bot
from nonebot.adapters.onebot.v11 import Message
from nonebot.params import CommandArg
import traceback
import time
from . import _lang
from . import _error
import json
from .account import multiAccoutData
import hashlib

try:
    import json5
except:
    json5 = json


def render_email(data, user_id):
    email =  _lang.text("email.email", [
        data['subject'],
        time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime()),
        data['from'],
        data["message"]], user_id)
    
    if data["items"]:
        email += _lang.text("email.items", [], user_id)
        length = 0
        for item in items.json2items(data["items"]):
            length += 1
            email += f'\n{length}. {item.data["display_name"]} x{item.count}'
    return email

async def submit_email(mail_data):
    users = os.listdir("data/etm")
    # 收集数据
    _user = []
    for rule in mail_data["rules"]:
        if rule[0] == "group":
            try:
                bot = get_bot(multiAccoutData[rule[1]])
            except:
                bot = list(get_bots().values())[0]
            group_member_list = await bot.get_group_member_list(group_id = rule[1])
            for user in group_member_list:
                _user.append(str(user["user_id"]))
                # print(_user)
            
    # 比对用户
    for user_id in users:
        if os.path.isdir(os.path.join("data", "etm", user_id)):
            for rule in mail_data["rules"]:
                match rule[0]:
                    case "group":
                        if user_id not in _user:
                            break
                    case "user":
                        if user_id != rule[1]:
                            break
                    case "bot":
                        pass # TODO
                if user_id not in data.emails.keys():
                    data.emails[user_id] = []
                data.emails[user_id].append(mail_data["id"])

@su.handle()
async def su_mail(event: MessageEvent, message: Message = CommandArg()) -> None:
    try:
        argv = message.extract_plain_text().splitlines()[0].strip().split(" ")
        if argv[0] in ["mail", "邮箱", "email"]:
            data = json.load(open("data/su.mails.json", encoding="utf-8"))
            if argv[1] in ["create"]:
                mail_id = hashlib.sha1(str(time.time()).encode("utf-8")).hexdigest()[:7]
                rules = []
                for arg in argv:
                    if arg.startswith("--"):
                        rules.append(arg[2:].split("="))
                data[mail_id] = {
                    "message": "\n".join(str(message).split("\n")[2:]),
                    "from": "XDBOT",
                    "subject": str(message).split("\n")[1],
                    "rules": rules,
                    "items": [],
                    "time": time.time(),
                    "id": mail_id
                }
                json.dump(data, open("data/su.mails.json", "w", encoding="utf-8"), ensure_ascii=False, indent=4)
                await su.finish(f"邮件 {mail_id} 创建成功")
            elif argv[1] in ["delete"]:
                if argv[2] in data.keys():
                    data.pop(argv[2])
                    json.dump(data, open("data/su.mails.json", "w", encoding="utf-8"), ensure_ascii=False, indent=4)
                    await su.finish(f"邮件 {argv[2]} 删除成功")
            elif argv[1] in ["edit"]:
                if len(argv) <= 3:
                    await su.finish(f"可编辑内容：{' '.join(data[argv[2]].keys())}")
                elif len(str(message).splitlines()) < 2:
                    await su.finish(f"{argv[2]}::{argv[3]} -> {data[argv[2]][argv[3]]}")
                elif argv[2] in data.keys():
                    data[argv[2]][argv[3]] = json5.loads("\n".join(message.extract_plain_text().splitlines()[1:]))
                    json.dump(data, open("data/su.mails.json", "w", encoding="utf-8"), ensure_ascii=False, indent=4)
                    await su.finish(f"邮件 {argv[2]} 编辑成功")
            elif argv[1] in ["view"]:
                await su.finish(render_email(data[argv[2]], event.get_user_id()))
            elif argv[1] in ["submit"]:
                await submit_email(data[argv[2]])
                await su.finish("完成！")    
    except:
        await _error.report(traceback.format_exc(), su)

@panel.handle()
@sign.handle()
async def unread_email_reminder(matcher: Matcher, event: MessageEvent):
    try:
        reminded_data = json.load(open("data/email.reminded.json", encoding="utf-8"))
        if data.emails.get(event.get_user_id()):
            email_count = 0
            for email in data.emails[event.get_user_id()]:
                if email not in (reminded_data.get(event.get_user_id()) or []):
                    email_count += 1
            if email_count != 0:
                await matcher.send(_lang.text("email.remind", [len(data.emails[event.get_user_id()])], event.get_user_id()))
                reminded_data[event.get_user_id()] = data.emails[event.get_user_id()]
    except:
        await _error.report(traceback.format_exc(), matcher)

