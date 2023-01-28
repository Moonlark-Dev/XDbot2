import json
import random
import time
import traceback
from . import _error
from nonebot import on_command
from nonebot.adapters.onebot.v11 import Message
from nonebot.adapters.onebot.v11.bot import Bot
from nonebot.adapters.onebot.v11.event import GroupMessageEvent
from nonebot.exception import FinishedException
from nonebot.params import CommandArg

jrrp = on_command("jrrp")
ctrlGroup = json.load(open("data/ctrl.json", encoding="utf-8"))["control"]


async def getJrrp(qq: str):
    data = json.load(open("data/jrrp.users.json"))
    if qq not in data.keys():
        await jrrp.send((
            "免责声明：\n"
            "人品所计算的结果并非与您有联系\n"
            "本插件所造成的一切损失请自己承担w！"), at_sender=True)
        data[qq] = {"max": 0}
    # 计算人品值
    random.seed(int(qq) + int(time.time() / 86400))
    luck = random.randint(0, 100)
    if luck > data[qq]["max"]:
        await jrrp.send(Message(f"[CQ:at,qq={qq}] 个人最高记录已刷新！"))
        data[qq]["max"] = luck
        json.dump(data, open("data/jrrp.users.json", "w"))
    # 生成提示文本
    if luck == 100:
        return "100,哎呦你干嘛"
    elif luck == 99:
        return "99！（可惜不是100, 小声bb）"
    elif 85 <= luck < 99:
        return f"{luck}，阁下好棒棒！~"
    elif 60 <= luck < 85:
        return f"{luck}，还行啦还行啦~"
    elif 45 <= luck < 60:
        return f"{luck}"
    elif 30 <= luck < 45:
        return f"{luck}，……"
    elif 15 <= luck < 30:
        return f"{luck}，呜哇——"
    elif 0 < luck < 15:
        return f"{luck}，呜哇——（没错，是百分制）"
    elif luck == 0:
        return f"{luck}！0！0！！！！！"
    else:
        return f"{luck}"


@jrrp.handle()
async def jrrpHandle(
        bot: Bot,
        event: GroupMessageEvent,
        message: Message = CommandArg()):
    try:
        argument = message.extract_plain_text().split(" ")
        if argument[0] == "":
            await jrrp.finish(
                message=f"你今天的人品值是：{await getJrrp(event.get_user_id())}",
                at_sender=True)
        elif argument[0] == "rank" or argument[0] == "今日排名":
            # 限时开启
            if time.localtime().tm_hour < 17:
                await jrrp.finish("人品排名将在每天服务器时间 17:00 准时开启")
            # 开始计算
            if argument.__len__() >= 2:
                count = int(argument[1])
            else:
                count = 10
            # 群成员列表
            userList = await bot.get_group_member_list(
                group_id=event.get_session_id().split("_")[1])
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
                                "jrrp": luck
                            }
                        )
                        inserted = True
                        break
                    length += 1
                if not inserted:
                    jrrpRank += [{"username": user["nickname"],
                                  "user_id": user["user_id"], "jrrp": luck}]
            # 生成rank
            nowRank = 0
            length = 0
            myRank = None
            myJrrp = -1
            qq = event.get_user_id()
            temp0 = 114514
            for r in jrrpRank:
                if r["jrrp"] != temp0:
                    nowRank += 1
                    temp0 = r["jrrp"]
                jrrpRank[length]["rank"] = nowRank
                # 检查是不是自己
                if str(r["user_id"]) == qq:
                    myRank = nowRank
                    myJrrp = jrrpRank[length]['jrrp']
                # 增加length
                length += 1
            # 生成文本
            text = "今日人品群排名：\n"
            for user in jrrpRank[:count]:
                text += f"{user['rank']}. {user['username']}: {user['jrrp']}\n"
            text += "-" * 20
            text += f"\n{myRank}. {(await bot.get_stranger_info(user_id=qq))['nickname']}: {myJrrp}"
            await jrrp.finish(text)
        else:
            await jrrp.finish(f"{argument[0]}今天的人品值是：{await getJrrp(argument[0])}")

    except FinishedException:
        raise FinishedException()
    except ValueError:
        await jrrp.finish("无效参数", at_sender=True)
    except Exception:
        await _error.report(traceback.format_exc(), jrrp)

# [HELPSTART] Version: 2
# Command: jrrp
# Usage: jrrp：计算自己的人品值
# Usage: jrrp <QQ号>：计算别人的人品值
# Usage: jrrp rank [count]：查询人品群排名（见jrrp(1)）
# Info: 计算自己或别人的人品值，或查询今日人品群排名
# Msg: 计算今日人品
# [HELPEND]
