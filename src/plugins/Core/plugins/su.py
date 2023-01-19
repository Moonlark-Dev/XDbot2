from nonebot.adapters.onebot.v11 import MessageEvent, Message
from nonebot.adapters.onebot.v11.bot import Bot
from nonebot import on_command
from nonebot.exception import FinishedException, IgnoredException
from nonebot.params import CommandArg
import traceback
import os
import time
import json
from . import _userCtrl
from nonebot.message import event_preprocessor
from nonebot.permission import SUPERUSER

su = on_command("su", aliases={"超管", "superuser"}, permission=SUPERUSER)
ctrlGroup = json.load(open("data/ctrl.json", encoding="utf-8"))["control"]
blackListData = json.load(open("data/su.blackList.json"))


def reloadBlackList():
    global blackListData
    blackListData = json.load(open("data/su.blackList.json"))


@su.handle()
async def suHandle(
        bot: Bot,
        message: Message = CommandArg()):
    try:
        argument = message.extract_plain_text().split(" ")
        if argument[0] == "ban" or argument[0] == "封禁":
            data = json.load(open("data/su.blackList.json"))
            if argument[1] not in data:
                data += [argument[1]]
                await su.send(f"已封禁{argument[1]}")
            # 广播
            groupList = await bot.get_group_list()
            if len(argument) >= 3:
                because = argument[2]
            else:
                because = "超管未指定原因"
            username = (await bot.get_stranger_info(user_id=argument[1]))['nickname']
            for group in groupList:
                await bot.send_group_msg(
                    message=f"用户 {username}({argument[1]}) 已被超管封禁：{because}",
                    group_id=group['group_id']
                )
            json.dump(data, open("data/su.blackList.json", "w"))
            reloadBlackList()
        elif argument[0] == "pardon" or argument[0] == "解封" or argument[0] == "unban":
            data = json.load(open("data/su.blackList.json"))
            length = 0
            for user in data:
                if user == argument[1]:
                    data.pop(length)
                    await su.send(f"已解封{argument[1]}")
                    break
                else:
                    length += 1
            json.dump(data, open("data/su.blackList.json", "w"))
            reloadBlackList()
        elif argument[0] == "call" or argument[0] == "调用":
            await su.send(
                await bot.call_api(
                    api=argument[1],
                    data=json.loads(argument[2])))
        elif argument[0] == "ct" or argument[0] == "发言排名":
            if argument[1] == "clear" or argument[1] == "清除数据":
                fileList = os.listdir("data")
                for file in fileList:
                    if file.startswith("ct."):
                        json.dump(dict(), open(f"data/{file}", "w"))
                        await su.send(f"已重置：{file}")
        elif argument[0] == "echo" or argument[0] == "调试输出":
            await su.send(
                Message(
                    message.extract_plain_text()[argument[0].__len__() + 1:]
                )
            )
        elif argument[0] == "notice" or argument[0] == "超级广播" or argument[0] == "广播":
            text = message.extract_plain_text()[argument[0].__len__() + 1:]
            groupList = await bot.get_group_list()
            # 开始广播
            for group in groupList:
                await bot.send_group_msg(
                    message=Message(f"【超级广播】\n{text}"),
                    group_id=group['group_id']
                )
        elif argument[0] == "config" or argument[0] == "配置":
            if argument[1] == "get" or argument[1] == "获取":
                await su.send(str(json.load(open(
                    f"data/{argument[2]}.json",
                    encoding="utf-8"
                ))[argument[3]]))
            elif argument[1] == "set" or argument == "设置":
                config = json.load(open(
                    f"data/{argument[2]}.json",
                    encoding="utf-8"))
                config[argument[3]] = json.loads(
                    message.extract_plain_text()[
                        len(argument[0] + argument[1] + argument[2] + argument[3]) + 4:]
                )
                json.dump(config, open(
                    f"data/{argument[2]}.json",
                    mode="w",
                    encoding="utf-8"
                ))
        elif argument[0] == "plugins" or argument[0] == "插件管理":
            config = json.load(
                open(
                    "data/init.disabled.json",
                    encoding="utf-8"))
            if argument[1] == "disable" or argument[1] == "禁用":
                if argument[2] not in config:
                    config += [argument[2]]
            elif argument[1] == "enable" or argument[1] == "启用":
                length = 0
                for conf in config:
                    if conf == argument[2]:
                        config.pop(length)
                        break
            json.dump(
                config,
                open(
                    "data/init.disabled.json",
                    "w",
                    encoding="utf-8"))
        elif argument[0] == "restart" or argument[0] == "重新启动":
            with open("data/reboot.py", "w") as f:
                f.write(str(time.time()))
        elif argument[0] == "cave" or argument[0] == "回声洞":
            if argument[1] == "remove" or argument[1] == "移除":
                data = json.load(open("data/cave.data.json", encoding="utf-8"))
                data['data'].pop(argument[2])
                json.dump(
                    data,
                    open(
                        "data/cave.data.json",
                        "w",
                        encoding="utf-8"))
        elif argument[0] == "give" or argument[0] == "给予":
            _userCtrl.addItem(
                argument[1], argument[2], int(
                    argument[3]), json.loads(
                    argument[4]))
        elif argument[0] == "forward" or argument[0] == "消息转发":
            data = json.load(
                open(
                    "data/forward.groupList.json",
                    encoding="utf-8"))
            if argument[1] == "add" or argument[1] == "添加群":
                data += [argument[2]]
            elif argument[1] == "remove" or argument[1] == "删除群":
                length = 0
                for group in data:
                    if group == argument[2]:
                        data.pop(length)
                    else:
                        length += 1
            json.dump(
                data,
                open(
                    "data/forward.groupList.json",
                    "w",
                    encoding="utf-8"))
        elif argument[0] == "shop" or argument[0] == "商店":
            shopData = json.load(
                open(
                    "data/shop.items.json",
                    encoding="utf-8"))
            if argument[1] == "remove" or argument[1] == "下架商品":
                item = shopData.pop(argument[2])
                if "from" not in item.keys():
                    # 用户出售商品
                    _userCtrl.addItem(str(
                        item["seller"]["user_id"]), item["item"]["id"], item["count"], item["item"]["data"])
                    json.dump(
                        shopData,
                        open(
                            "data/shop.items.json",
                            "w",
                            encoding="utf-8"))
                    # 通知卖家
                    msgList = json.load(
                        open(
                            "data/messenger.messageList.json",
                            encoding="utf-8"))
                    msgList += [{
                        "recv": str(item["seller"]["user_id"]),
                        "text": f"您出售的商品「{item['name']}」已被超管下架\n您获得了：「{item['name']}」 x{item['count']}",
                        "sender": {
                            "nickname": "X-D-B-O-T",
                            "user_id": 0
                        }
                    }]
                    json.dump(
                        msgList,
                        open(
                            "data/messenger.messageList.json",
                            "w",
                            encoding="utf-8"))
                elif item["from"] == "autosell":
                    # 系统出售商品
                    autoSellData = json.load(
                        open(
                            "data/autosell.items.json",
                            encoding="utf-8"))
                    length = 0
                    for itemData in autoSellData:
                        if itemData["id"] == item["item"]["id"] and itemData["data"] == item["item"]["data"]:
                            autosellItem = autoSellData.pop(length)
                            break
                        length += 1
                    json.dump(
                        autoSellData,
                        open(
                            "data/autosell.items.json",
                            "w",
                            encoding="utf-8"))
                    await su.send(f"自动出售商品已下架：\n{autosellItem}")
            elif argument[1] == "add" or argument[1] == "添加商品":
                data = json.load(
                    open(
                        "data/autosell.items.json",
                        encoding="utf-8"))
                data += {
                    "id": argument[2],
                    "count": int(argument[3]),
                    "price": int(argument[4]),
                    "info": None,
                    "data": json.loads(argument[5])
                }
                json.dump(
                    data,
                    open(
                        "data/autosell.items.json",
                        "w",
                        encoding="utf-8"))
                await su.send("商品已添加到自动出售任务清单！")
        elif argument[0] == "todo" or argument[0] == "代办":
            with open("TODO.txt", encoding="utf-8") as f:
                await su.send(f.read())
        elif argument[0] == "rule" or argument[0] == "自定义规则":
            if argument[1] == "import" or argument[1] == "导入":
                _code = message.extract_plain_text().split("\n")[1:]
                code = ""
                for c in _code:
                    code += c
                    code += "\n"
                code = json.loads(code)
                json.dump(rules, open(f"rules/{code}.json", encoding="utf-8"))
            elif argument[1] == "ls" or argument[1] == "查看全部":
                rules = os.listdir("rules")
                activeRules = []
                for r in rules:
                    if not r.startswith("_") and r.endswith(".json"):
                        activeRules += [r]
                await su.send(f"活动的规则：{activeRules}")
            elif argument[1] == "remove" or argument[1] == "删除":
                os.remove(f"rules/{argument[2]}.json")

        # 反馈
        await su.finish("完成")

    except FinishedException:
        raise FinishedException()
    except Exception:
        await bot.send_group_msg(
            message=traceback.format_exc(),
            group_id=ctrlGroup)
        await su.finish("处理失败")


@event_preprocessor
async def blackListHandle(
        bot: Bot,
        event: MessageEvent):
    try:
        if event.get_user_id() in blackListData:
            raise IgnoredException("Banned")

    except IgnoredException as e:
        raise IgnoredException(e)
    except Exception:
        await bot.send_group_msg(
            message=traceback.format_exc(),
            group_id=ctrlGroup)
