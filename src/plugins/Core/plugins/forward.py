import json
import traceback
from . import _error
from . import _lang
from nonebot import on_message
from nonebot.adapters.onebot.v11 import (Bot, GroupMessageEvent, Message,
                                         PrivateMessageEvent)

ctrlGroup = json.load(open("data/ctrl.json", encoding="utf-8"))["control"]
privateForward = on_message()
groupForward = on_message()


@privateForward.handle()
async def privateForwardHandle(
        bot: Bot,
        event: PrivateMessageEvent):
    try:
        await bot.send_group_msg(
            message=Message(
                f"""{_lang.text("forward.private")}
{_lang.text("forward._user")}{(await bot.get_stranger_info(user_id=event.get_user_id()))['nickname']} ({event.get_user_id()})
{event.get_message()}"""),
            group_id=ctrlGroup
        )

    except Exception:
        await _error.report(traceback.format_exc(), privateForward)


@groupForward.handle()
async def groupForwardHandle(
        bot: Bot,
        event: GroupMessageEvent):
    try:
        forwardData = json.load(open("data/forward.groupList.json"))
        if event.get_session_id().split("_")[1] in forwardData:
            await bot.send_group_msg(
                message=Message(
                    f"""{_lang.text("forward.group")}
{_lang.text("forward._group")}{event.get_session_id().split('_')[1]}
{_lang.text("forward._user")}{(await bot.get_stranger_info(user_id=event.get_user_id()))['nickname']} ({event.get_user_id()})
{event.get_message()}"""),
                group_id=ctrlGroup
            )

    except Exception:
        await _error.report(traceback.format_exc())
