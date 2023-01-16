import json
import traceback

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
                f"""「私聊信息转发」
用户：{(await bot.get_stranger_info(user_id=event.get_user_id()))['nickname']} ({event.get_user_id()})
{event.get_message()}"""),
            group_id=ctrlGroup
        )

    except Exception:
        await bot.send_group_msg(
            message=traceback.format_exc(),
            group_id=ctrlGroup)


@groupForward.handle()
async def groupForwardHandle(
        bot: Bot,
        event: GroupMessageEvent):
    try:
        forwardData = json.load(open("data/forward.groupList.json"))
        if event.get_session_id().split("_")[1] in forwardData:
            await bot.send_group_msg(
                message=Message(
                    f"""「群消息转发」
群聊：{event.get_session_id().split('_')[1]}
用户：{(await bot.get_stranger_info(user_id=event.get_user_id()))['nickname']} ({event.get_user_id()})
{event.get_message()}"""),
                group_id=ctrlGroup
            )

    except Exception:
        await bot.send_group_msg(
            message=traceback.format_exc(),
            group_id=ctrlGroup
        )
