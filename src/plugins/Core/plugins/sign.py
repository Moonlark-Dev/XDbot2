import json
import traceback
import random
import time
from nonebot import on_keyword
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent
from nonebot.exception import FinishedException
from . import _userCtrl

sign = on_keyword({"sign", "签到"})
# sign = on_command("sign", aliases={"签到"})
ctrlGroup = json.load(open("data/ctrl.json", encoding="utf-8"))["control"]


@sign.handle()
async def signHandle(
        bot: Bot,
        event: GroupMessageEvent):
    try:
        if event.get_plaintext().__len__() <= 5:
            latestSign = json.load(
                open(
                    "data/sign.latestTime.json",
                    encoding="utf-8"))
            signDay = json.load(
                open(
                    "data/sign.signDay.json",
                    encoding="utf-8"))
            userData = json.load(
                open(
                    "data/etm.userData.json",
                    encoding="utf-8"))
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
                        "buyTime": None,
                        "name": None,
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
            json.dump(
                signDay,
                open(
                    "data/sign.signDay.json",
                    "w",
                    encoding="utf-8"))
            json.dump(
                latestSign,
                open(
                    "data/sign.latestTime.json",
                    "w",
                    encoding="utf-8"))
            # 反馈结果
            await sign.finish(f"""+-----------------------------+
\t签到成功！
 「VimCoin」：{oldCoinCount} -> {oldCoinCount + addCoin} (+{addCoin})
 「经验」：{userData[userID]['exp']} -> {userData[userID]['exp'] + addExp} (+{addExp})
    您已连续签到{signDay[userID]}天
+-----------------------------+""")

    except FinishedException:
        raise FinishedException()
    except Exception:
        await bot.send_group_msg(
            message=traceback.format_exc(),
            group_id=ctrlGroup)
        await sign.finish("处理失败")

# [HELPSTART]
# !Usage 1 sign
# !Info 1 在 XDbot2 上签到
# [HELPEND]