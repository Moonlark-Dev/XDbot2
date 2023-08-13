import traceback
from nonebot.adapters import Bot
from nonebot.adapters.onebot.v11 import MessageEvent
from nonebot.exception import IgnoredException
from nonebot.message import event_preprocessor
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Message
from .su import su

# from .accout import multiAccoutData
from nonebot import get_bots
import json
from . import _error

blackListData = json.load(open("data/su.blackList.json", encoding="utf-8"))


@event_preprocessor
async def blackListHandle(event: MessageEvent):
    try:
        if event.get_user_id() in blackListData:
            raise IgnoredException("Banned")

    except IgnoredException as e:
        raise IgnoredException(e)
    except Exception:
        await _error.report(traceback.format_exc())


def reloadBlackList():
    global blackListData
    blackListData = json.load(open("data/su.blackList.json", encoding="utf-8"))


@su.handle()
async def su_pardon(message: Message = CommandArg()):
    argument = str(message).split(" ")
    try:
        if argument[0] in ["unban", "解封", "pardon"]:
            data = json.load(open("data/su.blackList.json", encoding="utf-8"))
            if argument[1] in data:
                data.pop(data.index(argument[1]))
                await su.send(f"已解封{argument[1]}")
            json.dump(data, open("data/su.blackList.json", "w", encoding="utf-8"))
            reloadBlackList()
    except BaseException:
        await _error.report(traceback.format_exc(), su)


@su.handle()
async def su_ban(bot: Bot, message: Message = CommandArg()):
    argument = str(message).split(" ")
    try:
        if argument[0] in ["ban", "封禁"]:
            data = json.load(open("data/su.blackList.json", encoding="utf-8"))
            if argument[1] not in data:
                data.append(argument[1])
                await su.send(f"已封禁{argument[1]}")
            json.dump(data, open("data/su.blackList.json", "w", encoding="utf-8"))
            reloadBlackList()

            # 广播
            try:
                if argument[2] in ["--disable-notice", "-d"]:
                    await su.finish()
            except KeyError:
                pass
            multiAccoutData = json.load(
                open("data/su.multiaccoutdata.ro.json", encoding="utf-8")
            )
            groupList = list(multiAccoutData.keys())
            if len(argument) >= 3:
                because = argument[2]
            else:
                because = "超管未指定原因"
            bots = get_bots()
            username = (await bot.get_stranger_info(user_id=argument[1]))["nickname"]
            for group in groupList:
                await bots[multiAccoutData[group]].send_group_msg(
                    message=f"用户 {username}({argument[1]}) 已被超管封禁：{because}",
                    group_id=group,
                )
    except BaseException:
        await _error.report(traceback.format_exc(), su)
