from nonebot.adapters.onebot.v11 import Message
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11.event import GroupMessageEvent
from nonebot.adapters.onebot.v11.bot import Bot
from nonebot import on_command
import random
import traceback
import json

jrrp = on_command("jrrp")
ctrlGroup = json.load(open("data/ctrl.json", encoding="utf-8"))["control"]


async def getJrrp(qq: str):
    data = json.load(open("data/jrrp.users.json"))
    if qq not in data.keys():
        await jrrp.send((
            "使用前须知：\n"
            "人品计算结果仅供娱乐，不代表现实中任何数值\n"
            "管理团队不承担任何由人品计算结果产生的后果！"), at_sender=True)
        data[qq] = {"max": 0}
    # 计算人品值
    random.seed(int(qq))
    luck = random.randint(0, 100)
    if luck > data[qq]["max"]:
        await jrrp.send(Message(f"[CQ:at,qq={qq}] 个人最高记录已刷新！"))
        data[qq]["max"] = luck
        json.dump(data, open("data/jrrp.users.json", "w"))
    # 生成提示文本
    if luck == 100:
        return "100！100！100！！！"
    elif luck == 99:
        return "99！（可惜不是100）"
    elif 85 <= luck < 99:
        return f"{luck}，是不错的的一天呢~"
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
async def jrrp_handle(
        bot: Bot,
        event: GroupMessageEvent,
        message: Message = CommandArg()):
    try:
        argument = message.extract_plain_text()
        if argument == "":
            await jrrp.finish(f"你今天的人品值是：{await getJrrp(event.get_user_id())}", at_sender=True)
        elif argument == "rank" or argument == "今日排名":
            userList = await bot.get_group_member_list(
                group_id=event.get_session_id().split("_")[1])
            # 计算排名
            jrrpRank = []
            for user in userList:
                random.seed(int(user["user_id"]))
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
                # 增加length
                length += 1
            # 生成文本
            text = "今日人品群排名：\n"
            for user in jrrpRank[:15]:
                text += f"{user['rank']}. {user['username']}\n"
            text += "-" * 20
            text += f"\n{myRank}. {(await bot.get_stranger_info(user_id=qq))['nickname']}"
            await jrrp.finish(text)
        else:
            await jrrp.finish(f"{argument}今天的人品值是：{await getJrrp(argument)}")
    except Exception as e:
        await bot.send_group_msg(
            message=traceback.format_exc(),
            group_id=ctrlGroup
        )
        await jrrp.finish(f"处理失败：{e}")





    
