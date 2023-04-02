import traceback
from nonebot.adapters.onebot.v11 import Bot, Message, MessageEvent
from nonebot.params import Command, CommandArg
from .su import su
from nonebot.log import logger
import time
import json
import os.path
from . import _error


def new_su_log_match(matcher):
    if not os.path.exists("data/su.log.json"):
        return ["暂未记录任何日志"]
    logs = json.load(open("data/su.log.json", encoding="utf-8"))
    ll = range(len(logs))
    reply = []
    for i in range(len(matcher)):
        m = matcher[i]
        if m.startswith("-Y"):
            m = m[2:]
            for l in ll:
                if logs[l]["time"]["Y"] != m:
                    logs[l] = {}
        elif m.startswith("-M"):
            m = m[2:]
            for l in ll:
                if logs[l]["time"]["M"] != m:
                    logs[l] = {}
        elif m.startswith("-D"):
            m = m[2:]
            for l in ll:
                if logs[l]["time"]["D"] != m:
                    logs[l] = {}
        elif m.startswith("-h"):
            m = m[2:]
            for l in ll:
                if logs[l]["time"]["h"] != m:
                    logs[l] = {}
        elif m.startswith("-m"):
            m = m[2:]
            for l in ll:
                if logs[l]["time"]["m"] != m:
                    logs[l] = {}
        elif m.startswith("-s"):
            m = m[2:]
            for l in ll:
                if logs[l]["time"]["s"] != m:
                    logs[l] = {}
        elif m.startswith("-u"):
            m = m[2:]
            for l in ll:
                if logs[l]["user"]["id"] != m:
                    logs[l] = {}
        elif m.startswith("-g"):
            m = m[2:]
            for l in ll:
                if logs[l]["user"]["group"] != m:
                    logs[l] = {}
        elif m.startswith("-c"):
            m = m[2:].replace("^", " ")
            for l in ll:
                if logs[l]["command"].find(m) == -1:
                    logs[l] = {}
    for i in logs:
        if i != {}:
            reply.append(
                f"{i['time']['Y']}/{i['time']['M']}/{i['time']['D']} - {i['time']['h']}:{i['time']['m']}:{i['time']['s']} - {i['user']['name']}({i['user']['id']}) - {i['command']}"
            )
    if not reply:
        reply.append("查询结果为空")
    return reply


def su_log_match(match, pf=""):
    if not os.path.exists("data/su.log.json"):
        return "暂未记录任何日志"
    logs = json.load(open("data/su.log.json", encoding="utf-8"))
    reply = ""
    try:
        tY = match[2]  # year
    except IndexError:
        reply += f"{pf}\n"
        for i in logs:
            reply += f"{i['time']['Y']}/{i['time']['M']}/{i['time']['D']} - {i['time']['h']}:{i['time']['m']}:{i['time']['s']} - {i['user']['name']}({i['user']['id']}) - {i['command']}\n"
        return reply
    try:
        tM = match[3]  # month
    except IndexError:
        reply += f"{pf}{tY}\n"
        for i in logs:
            if i["time"]["Y"] == tY:
                reply += f"{i['time']['Y']}/{i['time']['M']}/{i['time']['D']} - {i['time']['h']}:{i['time']['m']}:{i['time']['s']} - {i['user']['name']}({i['user']['id']}) - {i['command']}\n"
        return reply
    try:
        tD = match[4]  # day
    except IndexError:
        reply += f"{pf}{tY}/{tM}\n"
        for i in logs:
            if i["time"]["Y"] == tY and i["time"]["M"] == tM:
                reply += f"{i['time']['Y']}/{i['time']['M']}/{i['time']['D']} - {i['time']['h']}:{i['time']['m']}:{i['time']['s']} - {i['user']['name']}({i['user']['id']}) - {i['command']}\n"
        return reply
    try:
        th = match[5]  # hour
    except IndexError:
        reply += f"{pf}{tY}/{tM}/{tD}\n"
        for i in logs:
            if i["time"]["Y"] == tY and i["time"]["M"] == tM and i["time"]["D"] == tD:
                reply += f"{i['time']['h']}:{i['time']['m']}:{i['time']['s']} - {i['user']['name']}({i['user']['id']}) - {i['command']}\n"
        return reply
    try:
        tm = match[6]  # minute
    except IndexError:
        reply += f"{pf}{tY}/{tM}/{tD} {th}\n"
        for i in logs:
            if (
                i["time"]["Y"] == tY
                and i["time"]["M"] == tM
                and i["time"]["D"] == tD
                and i["time"]["h"] == th
            ):
                reply += f"{i['time']['h']}:{i['time']['m']}:{i['time']['s']} - {i['user']['name']}({i['user']['id']}) - {i['command']}\n"
        return reply
    try:
        ts = match[7]  # second
    except IndexError:
        reply += f"{pf}{tY}/{tM}/{tD} {th}:{tm}\n"
        for i in logs:
            if (
                i["time"]["Y"] == tY
                and i["time"]["M"] == tM
                and i["time"]["D"] == tD
                and i["time"]["h"] == th
                and i["time"]["m"] == tm
            ):
                reply += f"{i['time']['h']}:{i['time']['m']}:{i['time']['s']} - {i['user']['name']}({i['user']['id']}) - {i['command']}\n"
        return reply
    reply += f"{pf}{tY}/{tM}/{tD} {th}:{tm}:{ts}\n"
    for i in logs:
        if (
            i["time"]["Y"] == tY
            and i["time"]["M"] == tM
            and i["time"]["D"] == tD
            and i["time"]["h"] == th
            and i["time"]["m"] == tm
            and i["time"]["s"] == ts
        ):
            reply += f"{i['user']['name']}({i['user']['id']}) - {i['command']}\n"
    return reply


@su.handle()
async def su_xlog(message: Message = CommandArg()):
    argument = str(message).split(" ")
    try:
        if argument[0] in ["*log"]:
            argument.pop(0)
            reply = "XDbot2 审核日志 - 查询 " + " ".join(argument) + "\n"
            reply += "\n".join(new_su_log_match(argument))
            await su.send(reply)
    except BaseException:
        await _error.report(traceback.format_exc(), su)


@su.handle()
async def su_log(argument: list = str(Command()).split(" ")):
    try:
        if argument[0] in ["log", "日志", "审核日志", "查看日志"]:
            argn = len(argument)
            reply = "XDbot2 审核日志 - "
            _log_time = time.localtime()
            log_time = {
                "Y": time.strftime("%Y", _log_time),
                "M": time.strftime("%m", _log_time),
                "D": time.strftime("%d", _log_time),
                "h": time.strftime("%H", _log_time),
                "m": time.strftime("%M", _log_time),
                "s": time.strftime("%S", _log_time),
            }
            if argn == 1:
                reply += su_log_match(
                    ["", "", log_time["Y"], log_time["M"], log_time["D"]], "今日 "
                )
            elif argn == 2:
                if argument[1] in ["day", "今日", "本日", "日", "d", "D"]:
                    reply += su_log_match(
                        ["", "", log_time["Y"], log_time["M"], log_time["D"]], "今日 "
                    )
                elif argument[1] in ["month", "本月", "月", "m", "M"]:
                    reply += su_log_match(["", "",
                                          log_time["Y"], log_time["M"]], "本月 ")
                elif argument[1] in ["all", "所有", "全部", "a", "A"]:
                    # ********** xd我建议你过来写个合并转发 reply是全部文本(建议按行数分割) **********
                    reply += su_log_match(["", ""], "全部 ")
                else:
                    reply += "指定的查询参数无效"
            elif argn > 2:
                if argument[1] in ["match", "匹配"]:
                    reply += su_log_match(argument)
            await su.send(reply)
    except BaseException:
        await _error.report(traceback.format_exc(), su)


@su.handle()
async def write_su_logger(
    bot: Bot, event: MessageEvent, message: Message = CommandArg()
):
    log_msg = str(message)
    logger.debug(f"[su] 用户 {event.get_user_id()} 使用：{message}")
    try:
        if not log_msg.split(" ")[0] in ["log", "日志", "审核日志", "查看日志", "*log"]:
            if not os.path.exists("data/su.log.json"):
                json.dump([], open("data/su.log.json", "w", encoding="utf-8"))
            log = json.load(open("data/su.log.json", encoding="utf-8"))
            log_time = time.localtime()
            log.append(
                {
                    "user": {
                        "id": event.get_user_id(),
                        "name": (
                            await bot.get_stranger_info(
                                user_id=int(event.get_user_id())
                            )
                        )["nickname"],
                        "group": event.get_session_id().split("_")[1],
                    },
                    "time": {
                        "Y": time.strftime("%Y", log_time),
                        "M": time.strftime("%m", log_time),
                        "D": time.strftime("%d", log_time),
                        "h": time.strftime("%H", log_time),
                        "m": time.strftime("%M", log_time),
                        "s": time.strftime("%S", log_time),
                    },
                    "command": log_msg,
                }
            )
            json.dump(log, open("data/su.log.json", "w", encoding="utf-8"))
    except BaseException:
        logger.warning("[WARN] 记录su审核日志失败")
