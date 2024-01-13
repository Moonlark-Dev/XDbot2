import json
from ._utils import *
import random
import time
import traceback
from . import _error
from . import _lang
from nonebot import on_command
from nonebot.adapters.onebot.v11 import Message
from nonebot.adapters.onebot.v11.bot import Bot
from nonebot.adapters.onebot.v11.event import MessageEvent
from nonebot.exception import FinishedException
from nonebot.params import CommandArg

jrrp = on_command("jrrp")
ctrlGroup = json.load(open("data/ctrl.json", encoding="utf-8"))["control"]


async def getJrrp(qq: str):
    data = json.load(open("data/jrrp.users.json", encoding="utf-8"))
    if qq not in data.keys():
        await jrrp.send(_lang.text("jrrp.notice", [], qq), at_sender=True)
        data[qq] = {"max": 0}
    # 计算人品值
    random.seed(int(qq) + int((time.time() + 28800) / 86400))
    luck = random.randint(0, 100)
    if luck > data[qq]["max"]:
        await jrrp.send(
            Message(f"[CQ:at,qq={qq}] {_lang.text('jrrp.new_record',[],qq)}")
        )
        data[qq]["max"] = luck
        json.dump(data, open("data/jrrp.users.json", "w", encoding="utf-8"))
    # 生成提示文本
    if luck == 100:
        return _lang.text("jrrp.num.100", [luck], qq)
    elif luck == 99:
        return _lang.text("jrrp.num.99", [luck], qq)
    elif 85 <= luck < 99:
        return _lang.text("jrrp.num.85-99", [luck], qq)
    elif 60 <= luck < 85:
        return _lang.text("jrrp.num.60-85", [luck], qq)
    elif 45 <= luck < 60:
        return _lang.text("jrrp.num.45-60", [luck], qq)
    elif 30 <= luck < 45:
        return _lang.text("jrrp.num.30-45", [luck], qq)
    elif 15 <= luck < 30:
        return _lang.text("jrrp.num.15-30", [luck], qq)
    elif 0 < luck < 15:
        return _lang.text("jrrp.num.0-15", [luck], qq)
    elif luck == 0:
        return _lang.text("jrrp.num.0", [luck], qq)
    else:
        return _lang.text("jrrp.num.else", [luck], qq)


@jrrp.handle()
async def jrrpHandle(bot: Bot, event: MessageEvent, message: Message = CommandArg()):
    try:
        argument = str(message).split(" ")
        if argument[0] == "":
            await jrrp.finish(
                message=_lang.text(
                    "jrrp.today",
                    [await getJrrp(event.get_user_id())],
                    event.get_user_id(),
                ),
                at_sender=True,
            )
        elif argument[0] == "rank" or argument[0] == "今日排名":
            # 开始计算
            if argument.__len__() >= 2:
                count = int(argument[1])
            else:
                count = 10
            # 群成员列表
            userList = await bot.get_group_member_list(
                group_id=await get_group_id(event)
            )
            # 计算排名
            jrrpRank = []
            for user in userList:
                random.seed(int(user["user_id"]) + int(time.time() / 86400))
                luck = random.randint(0, 100)
                inserted = False
                length = 0
                for r in jrrpRank:
                    if r["jrrp"] < luck:
                        jrrpRank.insert(
                            length,
                            {
                                "username": user["nickname"],
                                "user_id": user["user_id"],
                                "jrrp": luck,
                            },
                        )
                        inserted = True
                        break
                    length += 1
                if not inserted:
                    jrrpRank += [
                        {
                            "username": user["nickname"],
                            "user_id": user["user_id"],
                            "jrrp": luck,
                        }
                    ]
            # 生成rank
            nowRank = 0
            length = 0
            temp1 = 1
            myRank = None
            myJrrp = -1
            qq = event.get_user_id()
            temp0 = 114514
            for r in jrrpRank:
                if r["jrrp"] != temp0:
                    nowRank += temp1
                    temp1 = 0
                    temp0 = r["jrrp"]
                jrrpRank[length]["rank"] = nowRank
                temp1 += 1
                # 检查是不是自己
                if str(r["user_id"]) == qq:
                    myRank = nowRank
                    myJrrp = jrrpRank[length]["jrrp"]
                # 增加length
                length += 1
            # 生成文本
            text = _lang.text("jrrp.group", [], event.get_user_id())
            for user in jrrpRank[:count]:
                text += f"{user['rank']}. {user['username']}: {user['jrrp']}\n"
            text += "-" * 20
            text += f"\n{myRank}. {(await bot.get_stranger_info(user_id=int(qq)))['nickname']}: {myJrrp}"
            await jrrp.finish(text)
        else:
            qq = argument[0]
            qq = qq.replace("[CQ:at,qq=", "").replace("]", "")
            await jrrp.finish(
                _lang.text("jrrp.other", [qq, await getJrrp(qq)], event.get_user_id())
            )

    except FinishedException:
        raise FinishedException()
    except ValueError:
        await jrrp.finish(
            _lang.text("jrrp.error", [], event.get_user_id()), at_sender=True
        )
    except Exception:
        await _error.report(traceback.format_exc())


# [HELPSTART] Version: 2
# Command: jrrp
# Usage: jrrp：计算自己的人品值
# Usage: jrrp <QQ号>：计算别人的人品值
# Usage: jrrp rank [count]：查询人品群排名（见jrrp(1)）
# Info: 计算自己或别人的人品值，或查询今日人品群排名
# Msg: 计算今日人品
# [HELPEND]
