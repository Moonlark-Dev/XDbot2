'''
from nonebot.adapters.onebot.v11 import MessageEvent, Message, GroupMessageEvent
from nonebot.adapters.onebot.v11.event import GroupRequestEvent
from nonebot.adapters.onebot.v11.bot import Bot
from nonebot import on_command, get_bots, on_type, get_driver
from nonebot.exception import FinishedException, IgnoredException
from . import _smart_reply as smart_reply
from nonebot.params import CommandArg
from . import _messenger as messenger
import traceback
import os
import time
from . import _error
import json
from . import _lang
from . import _userCtrl
from nonebot.message import event_preprocessor
from nonebot.permission import SUPERUSER

# 可选依赖
try:
    import pyautogui
except ImportError:
    pass

su = on_command("su", aliases={"超管", "superuser"}, permission=SUPERUSER)
accout_manager = on_command("accout", aliases={"多帐号"})

ctrlGroup = json.load(open("data/ctrl.json", encoding="utf-8"))["control"]
blackListData = json.load(open("data/su.blackList.json", encoding="utf-8"))
multiAccoutData = {}
group_request = on_type(GroupRequestEvent)
bots = []
priority_accout = json.load(
    open(
        "data/su.priority_accout.json",
        encoding="utf-8"))
driver = get_driver()
accouts = {}
su_notice_cache = ""


def parseCave(text: str):
    imageIDStart = text.find("[[Img:")
    if imageIDStart == -1:
        return text
    else:
        imageID = text[imageIDStart + 6: text.find("]]]", imageIDStart)]
        imagePath = os.path.join(
            os.path.abspath("."),
            "data",
            "caveImages",
            f"{imageID}.png")
        imageCQ = f"[CQ:image,file=file://{imagePath}]"
        return parseCave(text.replace(f"[[Img:{imageID}]]]", str(imageCQ)))


@driver.on_bot_connect
@driver.on_bot_disconnect
async def reloadMuiltData():
    global multiAccoutData, bots, accouts
    bots = get_bots()
    accouts = {}
    multiAccoutData = {}
    for key in list(bots.keys()):
        bot = bots[key]
        groups = await bot.get_group_list()
        for group in groups:
            if group["group_id"] not in accouts.keys():
                accouts[group["group_id"]] = [key]
            else:
                accouts[group["group_id"]].append(key)
            if group["group_id"] not in multiAccoutData.keys():
                multiAccoutData[group["group_id"]] = key
            elif key in priority_accout["accouts"]:
                multiAccoutData[group["group_id"]] = key
    json.dump(
        multiAccoutData,
        open(
            "data/su.multiaccoutdata.ro.json",
            "w",
            encoding="utf-8"))


@accout_manager.handle()
async def mulitaccout_manager(
        event: GroupMessageEvent,
        message: Message = CommandArg()):
    global multiAccoutData
    try:
        argument = str(message).split(" ")
        qq = event.get_user_id()
        if argument[0] == "set":
            if argument[1] in accouts[event.group_id]:
                multiAccoutData[event.group_id] = argument[1]
                json.dump(
                    multiAccoutData, open(
                        "data/su.multiaccoutdata.ro.json", "w", encoding="utf-8"))
                await accout_manager.finish(_lang.text("su.set_accout_success", [argument[1]], qq))
            else:
                await accout_manager.finish(_lang.text("su.accout_not_found"), user=qq)
        elif argument[0] == "list":
            await accout_manager.finish(_lang.text("su.accout_list", [accouts[event.group_id]], qq))
        elif argument[0] == "reload":
            await reloadMuiltData()

    except FinishedException:
        raise FinishedException()
    except BaseException:
        await _error.report(traceback.format_exc(), accout_manager)


@su.handle()
async def suHandle(bot: Bot, event: MessageEvent, message: Message = CommandArg()):
    try:  # 记录审核日志
        log_msg = str(message)
        if not log_msg.split(" ")[0] in ["log", "日志", "审核日志", "查看日志", "*log"]:
            if not os.path.exists("data/su.log.json"):
                json.dump([], open("data/su.log.json", "w", encoding="utf-8"))
            log = json.load(open("data/su.log.json", encoding="utf-8"))
            log_time = time.localtime()
            log.append({
                "user": {
                    "id": event.get_user_id(),
                    "name": (await bot.get_stranger_info(user_id=int(event.get_user_id())))["nickname"],
                    "group": event.get_session_id().split("_")[1]
                },
                "time": {
                    "Y": time.strftime("%Y", log_time),
                    "M": time.strftime("%m", log_time),
                    "D": time.strftime("%d", log_time),
                    "h": time.strftime("%H", log_time),
                    "m": time.strftime("%M", log_time),
                    "s": time.strftime("%S", log_time)
                },
                "command": log_msg
            })
            json.dump(log, open("data/su.log.json", "w", encoding="utf-8"))
    except BaseException:
        print("[WARN] 记录su审核日志失败")
    try:
        argument = str(message).split(" ")
        if argument[0] == "ban" or argument[0] == "封禁":
            data = json.load(open("data/su.blackList.json", encoding="utf-8"))
            if argument[1] not in data:
                data += [argument[1]]
                await su.send(f"已封禁{argument[1]}")
            # 广播
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
            json.dump(
                data,
                open(
                    "data/su.blackList.json",
                    "w",
                    encoding="utf-8"))
            reloadBlackList()
        elif argument[0] == "pardon" or argument[0] == "解封" or argument[0] == "unban":
            data = json.load(open("data/su.blackList.json", encoding="utf-8"))
            length = 0
            for user in data:
                if user == argument[1]:
                    data.pop(length)
                    await su.send(f"已解封{argument[1]}")
                    break
                else:
                    length += 1
            json.dump(
                data,
                open(
                    "data/su.blackList.json",
                    "w",
                    encoding="utf-8"))
            reloadBlackList()
        elif argument[0] == "notice" or argument[0] == "超级广播" or argument[0] == "广播":
            global su_notice_cache
            text = str(message)[argument[0].__len__() + 1:]
            if text == "submit":
                if su_notice_cache != "":
                    groupList = list(multiAccoutData.keys())
                    bots = get_bots()
                    # 开始广播
                    for group in groupList:
                        await bots[multiAccoutData[group]].send_group_msg(
                            message=Message(f"【超级广播】\n{su_notice_cache}"),
                            group_id=group,
                        )
                    su_notice_cache = ""
                else:
                    await su.finish("请先使用 /su notice <context> 设定超级广播内容")
            elif text == "drop":
                su_notice_cache = ""
                await su.finish("超级广播内容已清除")
            elif text == "get":
                await su.finish(su_notice_cache)
            else:
                su_notice_cache = text
                await su.finish("超级广播内容已设定")

            elif argument[1] == "set" or argument == "设置":
                config = json.load(
                    open(
                        f"data/{argument[2]}.json",
                        encoding="utf-8"))
                config[argument[3]] = json.loads(
                    message.extract_plain_text()[
                        len(argument[0] + argument[1] + argument[2] + argument[3]) + 4:
                    ]
                )
                json.dump(
                    config, open(
                        f"data/{argument[2]}.json", mode="w", encoding="utf-8")
                )
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
            elif argument[0] == "cave" or argument[0] == "回声洞":
            if argument[1] in ["comment", "reply", "回复"]:
                if argument[2] in ["remove", "rm", "删除"]:
                    data = json.load(
                        open(
                            "data/cave.comments.json",
                            encoding="utf-8"))
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
                cave_data = data["data"].pop(argument[2])
                await su.send(Message((
                    f"回声洞——（{cave_data['id']}）\n"
                    f"{parseCave(cave_data['text'])}\n"
                    f"——{(await bot.get_stranger_info(user_id=cave_data['sender']))['nickname']}（{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(cave_data['time']))}）"
                )))
                json.dump(
                    data,
                    open(
                        "data/cave.data.json",
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
        elif argument[0] == "give" or argument[0] == "给予":
            _userCtrl.addItem(
                argument[1], argument[2], int(
                    argument[3]), json.loads(
                    argument[4])
            )
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
                    _userCtrl.addItem(
                        str(item["seller"]["user_id"]),
                        item["item"]["id"],
                        item["count"],
                        item["item"]["data"],
                    )
                    json.dump(
                        shopData, open(
                            "data/shop.items.json", "w", encoding="utf-8")
                    )
                    # 通知卖家
                    msgList = json.load(
                        open(
                            "data/messenger.messageList.json",
                            encoding="utf-8")
                    )
                    msgList += [
                        {
                            "recv": str(item["seller"]["user_id"]),
                            "text": f"您出售的商品「{item['name']}」已被超管下架\n您获得了：「{item['name']}」 x{item['count']}",
                            "sender": {"nickname": "X-D-B-O-T", "user_id": 0},
                        }
                    ]
                    json.dump(
                        msgList,
                        open(
                            "data/messenger.messageList.json",
                            "w",
                            encoding="utf-8"),
                    )
                elif item["from"] == "autosell":
                    # 系统出售商品
                    autoSellData = json.load(
                        open("data/autosell.items.json", encoding="utf-8")
                    )
                    length = 0
                    for itemData in autoSellData:
                        if (
                            itemData["id"] == item["item"]["id"]
                            and itemData["data"] == item["item"]["data"]
                        ):
                            autosellItem = autoSellData.pop(length)
                            break
                        length += 1
                    json.dump(
                        autoSellData,
                        open(
                            "data/autosell.items.json",
                            "w",
                            encoding="utf-8"),
                    )
                    await su.send(f"自动出售商品已下架：\n{autosellItem}")
            elif argument[1] == "add" or argument[1] == "添加商品":
                data = json.load(
                    open(
                        "data/autosell.items.json",
                        encoding="utf-8"))
                try:
                    s_nickname = argument[7]
                    s_user_id = argument[8]
                except IndexError:
                    s_nickname = "System"
                    s_user_id = "AdminShop"
                data.append(
                    {
                        "id": argument[2],
                        "count": int(argument[3]),
                        "price": int(argument[4]),
                        "info": None,
                        "data": json.loads(argument[5]),
                        "nickname": s_nickname,
                        "user_id": s_user_id,
                    }
                )
                try:
                    data[-1]["maxBuy"] = int(argument[6])
                except IndexError:
                    pass
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

        elif argument[0] in ["reply", "调教"]:
            if argument[1] in ["global"]:
                reply_id = argument[2]
                smart_reply.global_reply(reply_id)
            elif argument[1] in ["remove", "rm", "删除"]:
                smart_reply.remove_reply(
                    argument[2], event.get_user_id(), True)
               elif argument[0] in ["ma", "multiaccout", "多账户"]:
            if argument[1] in ["status", "状态"]:
                reply = "「XDbot2 Multi-Accout 账户列表」\n"
                bots = get_bots()
                reply += f"已连接账户：{len(bots.keys())}\n"
                length = 1
                for accout in list(bots.keys()):
                    userData = await bot.get_stranger_info(
                        user_id=str((await bots[accout].get_login_info())["user_id"])
                    )
                    reply += (
                        f"{length}. {userData['nickname']} ({userData['user_id']})\n"
                    )
                    length += 1
                await su.send(reply)
                # 分配情况
                length = 1
                reply = "「XDbot2 Multi-Accout 群聊分配」\n"
                for group in list(multiAccoutData.keys()):
                    reply += f"{length}. {group}: {multiAccoutData[group]}\n"
                    length += 1
                await su.send(reply)

        # 反馈
        await su.finish("完成")

    except FinishedException:
        raise FinishedException()
    except Exception:
        await _error.report(traceback.format_exc(), su)


@event_preprocessor
async def blackListHandle(bot: Bot, event: MessageEvent):
    try:
        if event.get_user_id() in blackListData:
            raise IgnoredException("Banned")

    except IgnoredException as e:
        raise IgnoredException(e)
    except Exception:
        await bot.send_group_msg(message=traceback.format_exc(), group_id=ctrlGroup)





@group_request.handle()
async def group_request_handle(
        bot: Bot,
        event: GroupRequestEvent):
    try:
        if event.sub_type == "invite":
            await bot.send_group_msg(
                message=(
                    "「被邀请加群」\n"
                    f"群号：{event.group_id}\n"
                    f"用户：{event.user_id}"),
                group_id=ctrlGroup)
            await event.approve(bot)
            await reloadMuiltData()

    except BaseException:
        await _error.report(traceback.format_exc())
'''

# # [HELPSTART] Version: 2
# # Command: su
# # Info: XDbot2超级管理员操作，详见su(0)
# # Msg: 超管快捷操作
# # Usage: su ban <QQ号>：封禁用户，见su(1)
# # Usage: su pardon <QQ号>：解封用户
# # Usage: su plugin enable <插件名>：启用插件（su(2)）
# # Usage: su plugin disable <插件名>：禁用插件
# # Usage: su restart：重启XDbot2
# # Usage: su call <API终结点>\n<数据(json)>：调用 go-cqhttp API（su(4)）
# # Usage: su config set <配置项名> <键> <值(json)>：修改配置（su(5)）
# # Usage: su config get <配置项名> <键>：获取配置值（su(6)）
# # Usage: su ct clear：清除发言排名数据
# # Usage: su echo <文本>：发送文本
# # Usage: su cave remove <回声洞ID>：删除回声洞（su(9)）
# # Usage：我tm不想写了自己去看/man把艹
# # [HELPEND]
