from nonebot.adapters import Bot
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Message
from .su import su
from .cave import parseCave
from ._error import report
import traceback
import json
import time
from . import _messenger


@su.handle()
async def cave(bot: Bot, message: Message = CommandArg()):
    try:
        argument = str(message).split(" ")
        if argument[0] == "cave" or argument[0] == "回声洞":
            if argument[1] in ["ban", "封禁"]:
                data = json.load(
                    open("data/cave.banned.json", encoding="utf-8"))
                data.append(argument[2])
                json.dump(data, open(
                    "data/cave.banned.json", "w", encoding="utf-8"))
                await su.finish(f"已移除 {argument[2]} 的 cave.add 权限")
            elif argument[1] in ["unban", "pardon", "解封"]:
                data = json.load(
                    open("data/cave.banned.json", encoding="utf-8"))
                data.pop(data.index(argument[2]))
                json.dump(data, open(
                    "data/cave.banned.json", "w", encoding="utf-8"))
                await su.finish(f"已为 {argument[2]} 添加 cave.add 权限")
            elif argument[1] in ["comment", "reply", "回复"]:
                if argument[2] in ["remove", "rm", "删除"]:
                    data = json.load(
                        open(
                            "data/cave.comments.json",
                            encoding="utf-8"))
                    _messenger.send_message(
                        f"您在 Cave#{argument[3]} 下的评论 #{argument[4]} 已被删除",
                        data[argument[3]]["data"][argument[4]]["sender"])
                    data[argument[3]]["data"].pop(argument[4])
                    json.dump(
                        data,
                        open(
                            "data/cave.comments.json",
                            "w",
                            encoding="utf-8"))
                    await su.send(f"已删除 Cave{argument[3]}#{argument[4]}")
            elif argument[1] == "remove" or argument[1] == "移除":
                data = json.load(open("data/cave.data.json", encoding="utf-8"))
                restore_data = json.load(
                    open("data/cave.data.restore.json", encoding="utf-8"))
                cave_data = data["data"].pop(argument[2])
                restore_data[argument[2]] = cave_data
                await su.send(Message((
                    f"回声洞——（{cave_data['id']}）\n"
                    f"{parseCave(cave_data['text'])}\n"
                    f"——{(await bot.get_stranger_info(user_id=cave_data['sender']))['nickname']}（{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(cave_data['time']))}）"
                )))
                _messenger.send_message(
                    f"您投稿的 Cave#{argument[2]} 已被删除",
                    cave_data["sender"])
                json.dump(
                    data,
                    open(
                        "data/cave.data.json",
                        "w",
                        encoding="utf-8"))
                json.dump(
                    restore_data,
                    open(
                        "data/cave.data.restore.json",
                        "w",
                        encoding="utf-8"))
                await su.send(f"已删除回声洞（{cave_data['id']}）")
            elif argument[1] in ["add", "添加"]:
                data = json.load(open("data/cave.data.json", encoding="utf-8"))
                data["data"][str(data["count"])] = {
                    "id": str(data["count"]),
                    "text": argument[2].replace("%20", " ").replace(r"\n", "\n"),
                    "sender": {"type": "unknown"},
                }
                data["count"] += 1
                json.dump(
                    data,
                    open(
                        "data/cave.data.json",
                        "w",
                        encoding="utf-8"))
            elif argument[1] in ["modify", "修改"]:
                data = json.load(open("data/cave.data.json", encoding="utf-8"))
                if argument[3] == "sender":
                    if argument[4] in ["name", "nickname"]:
                        data["data"][argument[2]]["sender"] = {
                            "type": "nickname",
                            "name": argument[5],
                        }
                    elif argument[4] in ["id", "qq"]:
                        data["data"][argument[2]]["sender"] = argument[5]
                    elif argument[4] in ["unknown", "unkown"]:
                        data["data"][argument[2]]["sender"] = {
                            "type": "unknown"}
                elif argument[3] == "text":
                    data["data"][argument[2]]["text"] = (
                        argument[4].replace("%20", " ").replace(r"\n", "\n")
                    )
                json.dump(
                    data,
                    open(
                        "data/cave.data.json",
                        "w",
                        encoding="utf-8"))
            elif argument[1] in ["restore", "恢复"]:
                data = json.load(open("data/cave.data.json", encoding="utf-8"))
                restore_data = json.load(
                    open("data/cave.data.restore.json", encoding="utf-8"))
                cave_data = restore_data.pop(argument[2])
                data["data"][argument[2]] = cave_data
                await su.send(f"已恢复回声洞（{cave_data['id']}）")
                await su.send(Message((
                    f"回声洞——（{cave_data['id']}）\n"
                    f"{parseCave(cave_data['text'])}\n"
                    f"——{(await bot.get_stranger_info(user_id=cave_data['sender']))['nickname']}（{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(cave_data['time']))}）"
                )))
                json.dump(data, open(
                    "data/cave.data.json", "w", encoding="utf-8"))
                json.dump(restore_data, open(
                    "data/cave.data.restore.json", "w", encoding="utf-8"))
    except BaseException:
        await report(traceback.format_exc(), su)
