import json
import traceback
import random
import time
from . import _error
from nonebot import on_keyword, on_command
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, Message
from nonebot.exception import FinishedException
from nonebot.params import CommandArg
from . import _userCtrl

sign = on_keyword({"sign", "签到"})
signrank = on_command("sign", aliases={"签到"})
ctrlGroup = json.load(open("data/ctrl.json", encoding="utf-8"))["control"]


@signrank.handle()
async def signrankHandle(bot: Bot,
                         event: GroupMessageEvent,
                         args: Message = CommandArg()):
    args = args.extract_plain_text().split(" ")
    if not args[0] == "rank":
        return
    rank = "今日签到排行榜：\n"
    try:
        with open("data/sign.rank.json", "r") as f:
            sign_rank_data = json.load(f)
            if sign_rank_data["day"] != int(time.time() / 86400):
                raise FileNotFoundError
    except BaseException:
        sign_rank_data = {"day": int(time.time() / 86400), "rank": []}
    if not sign_rank_data["rank"]:
        await signrank.finish("今天还没有人签到！")
    num = 0
    me = "你今天还没有签到！"
    for i in sign_rank_data["rank"]:
        num += 1
        rank += f"{str(num)}. {(await bot.get_stranger_info(user_id=i['qq']))['nickname']}（{i['time']}）\n"
        if i["qq"] == int(event.get_user_id()):
            me = f"{str(num)}. {(await bot.get_stranger_info(user_id=i['qq']))['nickname']}（{i['time']}）"
    rank += "--------------------\n" + me
    await signrank.finish(rank)


@sign.handle()
async def signHandle(bot: Bot, event: GroupMessageEvent):
    try:
        if event.get_plaintext().__len__() <= 5:
            latestSign = json.load(
                open("data/sign.latestTime.json", encoding="utf-8"))
            signDay = json.load(
                open("data/sign.signDay.json", encoding="utf-8"))
            userData = json.load(
                open("data/etm.userData.json", encoding="utf-8"))
            userID = event.get_user_id()
            # 检查数据是否存在
            if userID not in list(latestSign.keys()):
                latestSign[userID] = 0
            if userID not in list(signDay.keys()):
                signDay[userID] = 0
            if userID not in list(userData.keys()):
                userData[userID] = {
                    "level": 1,
                    "exp": 0,
                    "vip": {
                        "endTime": None,
                        "level": None
                    }
                }
            # 修改数据
            if latestSign[userID] == int(time.time() / 86400):
                await sign.finish("您已经签到过了", at_sender=True)
            if latestSign[userID] - int(time.time() / 86400) == -1:
                signDay[userID] += 1
            else:
                signDay[userID] = 0
            latestSign[userID] = int(time.time() / 86400)
            # 基础随机奖励
            addCoin = random.randint(0, 15)
            addExp = random.randint(1, 10)
            # 连续签到加成
            addCoin *= 1 + signDay[userID] / 100
            addExp *= 1 + signDay[userID] / 100
            # 等级加成
            addCoin *= 1 + userData[userID]["level"] / 2 / 10
            addExp *= 1 + userData[userID]["level"] / 2 / 10
            # VIP加成
            if userData[userID]["vip"]["level"]:
                addCoin *= 1 + userData[userID]["vip"]["level"] / 2
                addExp *= 1 + userData[userID]["vip"]["level"] / 2
            # 实际收入
            addCoin /= 2
            addExp /= 1.5
            addCoin = int(addCoin)
            addExp = int(addExp)
            # 修改数据
            oldCoinCount = _userCtrl.getCountOfItem(userID, "0")
            _userCtrl.addItem(userID, "0", addCoin, dict())
            _userCtrl.addExp(userID, addExp)
            # 保存数据
            json.dump(signDay,
                      open("data/sign.signDay.json", "w", encoding="utf-8"))
            json.dump(latestSign,
                      open("data/sign.latestTime.json", "w", encoding="utf-8"))
            try:
                with open("data/sign.rank.json", "r") as f:
                    sign_rank_data = json.load(f)
                    if sign_rank_data["day"] != int(time.time() / 86400):
                        raise FileNotFoundError
            except BaseException:
                sign_rank_data = {"day": int(time.time() / 86400), "rank": []}
            sign_rank_data["rank"].append({
                "qq":
                int(event.get_user_id()),
                "time":
                time.strftime("%H:%M:%S", time.localtime())
            })
            with open("data/sign.rank.json", "w") as f:
                json.dump(sign_rank_data, f)
            # 反馈结果
            await sign.finish(f"""+-----------------------------+
\t签到成功！
 「VimCoin」：{oldCoinCount} -> {oldCoinCount + addCoin} (+{addCoin})
 「经验」：{userData[userID]['exp']} -> {userData[userID]['exp'] + addExp} (+{addExp})
    您已连续签到{signDay[userID]}天
    您是今天第{len(sign_rank_data['rank'])}个签到的
+-----------------------------+""")

    except FinishedException:
        raise FinishedException()
    except Exception:
        await _error.report(traceback.format_exc(), sign)


# [HELPSTART]
# !Usage 1 sign
# !Info 1 在 XDbot2 上签到
# [HELPEND]
