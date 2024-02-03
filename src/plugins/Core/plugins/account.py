import json
from nonebot import on_command, get_driver, get_bots
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, Message
from nonebot.adapters.onebot.v11 import Event
from nonebot.exception import IgnoredException
from nonebot.message import event_preprocessor
from nonebot.params import CommandArg
from . import _lang
from . import _error
import traceback
import json
from .su import su

ctrlGroup = json.load(open("data/ctrl.json", encoding="utf-8"))["control"]
priority_accout = json.load(open("data/su.priority_accout.json", encoding="utf-8"))
accounts = {}
multiAccountData = {}
account_manager = on_command("accout", aliases={"多帐号", "account"})
driver = get_driver()


def get_accounts_data() -> dict:
    return multiAccountData


@event_preprocessor
async def multiAccoutManager(bot: Bot, event: Event):
    try:
        group_id = int(event.get_session_id().split("_")[1])
    except IndexError:
        return
    if group_id in multiAccountData.keys() and str(bot.self_id) != multiAccountData[group_id]:
        raise IgnoredException("多帐号：忽略")


@su.handle()
async def get_multiaccount_data(bot: Bot, message: Message = CommandArg()):
    try:
        argument = str(message).split(" ")
        if argument[0] in ["ma", "multiaccout", "account", "多账户"]:
            if argument[1] in ["status", "状态"]:
                reply = "「XDbot2 Multi-Account 账户列表」\n"
                bots = get_bots()
                reply += f"已连接账户：{len(bots.keys())}\n"
                length = 1
                for account in list(bots.keys()):
                    userData = await bot.get_stranger_info(
                        user_id=(await bots[account].get_login_info())["user_id"]
                    )
                    reply += (
                        f"{length}. {userData['nickname']} ({userData['user_id']})\n"
                    )
                    length += 1
                await su.send(reply)
                # 分配情况
                length = 1
                reply = "「XDbot2 Multi-Account 群聊分配」\n"
                for group in list(multiAccountData.keys()):
                    reply += f"{length}. {group}: {multiAccountData[group]}\n"
                    length += 1
                await su.finish(reply)
    except BaseException:
        await _error.report(traceback.format_exc(), su)


@driver.on_bot_connect
@driver.on_bot_disconnect
async def reloadMuiltData():
    global multiAccountData, bots, accounts
    bots = get_bots()
    accounts = {}
    multiAccountData = {}
    for key in list(bots.keys()):
        bot = bots[key]
        groups = await bot.get_group_list()
        for group in groups:
            if group["group_id"] not in accounts.keys():
                accounts[group["group_id"]] = [key]
            else:
                accounts[group["group_id"]].append(key)
            if group["group_id"] not in multiAccountData.keys():
                multiAccountData[group["group_id"]] = key
            elif key in priority_accout["accouts"]:
                multiAccountData[group["group_id"]] = key
    json.dump(
        multiAccountData, open("data/su.multiaccoutdata.ro.json", "w", encoding="utf-8")
    )


@account_manager.handle()
async def mulitaccout_manager(
    event: GroupMessageEvent, message: Message = CommandArg()
):
    global multiAccountData
    try:
        argument = str(message).split(" ")
        qq = event.get_user_id()
        if argument[0] == "set":
            if argument[1] in accounts[event.group_id]:
                multiAccountData[event.group_id] = argument[1]
                json.dump(
                    multiAccountData,
                    open("data/su.multiaccoutdata.ro.json", "w", encoding="utf-8"),
                )
                await account_manager.finish(
                    _lang.text("su.set_accout_success", [argument[1]], qq)
                )
            else:
                await account_manager.finish(_lang.text("su.accout_not_found"), user=qq)
        elif argument[0] == "list":
            await account_manager.finish(
                _lang.text("su.accout_list", [accounts[event.group_id]], qq)
            )
        elif argument[0] == "reload":
            await reloadMuiltData()
            await account_manager.finish("已重载多账号分配")

    except BaseException:
        await _error.report(traceback.format_exc(), account_manager)
