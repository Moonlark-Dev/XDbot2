from . import _error
from nonebot import on_command, on_regex, on_message
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Bot
from ._utils import Json
import time
import re

@on_regex(r"\[CQ:at,qq=([0-9]+|all)\]").handle()
async def at_handle(bot: Bot, event: GroupMessageEvent):
    try:
        at_user_id = re.search(r"\[CQ:at,qq=([0-9]+|all)\]", str(event.get_message()))\
            .group(0)\
                .replace("[CQ:at,qq=", "")\
                    .replace("]", "")
        event_data = {
            "time": time.time(),
            "group_id": event.group_id,
            "user_id": event.user_id
        }
        
        # 获取历史消息
        messages = []
        _messages = (await bot.call_api(
            "get_group_msg_history",
            # message_seq=event.message_id,
            group_id=event.group_id
        ))["messages"]
        for message in _messages:
            messages.append(message["message_id"])
        event_data["messages"] = messages

        data = Json(f"who_at_me.data.json")
        data.get(at_user_id, []).append(event_data)
        
    except: 
        await _error.report()
