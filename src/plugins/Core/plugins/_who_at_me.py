"""
from . import _error
from nonebot.matcher import Matcher
from . import _lang
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
        data = Json("who_at_me.data.json")
        data.get(at_user_id, []).append(event_data)

        need_message = 19
        
        @on_message().handle()
        async def _(matcher: Matcher, sub_event: GroupMessageEvent):
            try:
                if sub_event.group_id == event.group_id:
                    
    except: 
        await _error.report()

@on_command("who-at-me").handle()
async def whoatme_handler(bot: Bot, event: GroupMessageEvent):
    try:
        user_data = Json("who_at_me.data.json")[str(event.user_id)]
        # TODO Notice信息
        node_messages = []
        for item in user_data:
            sub_node = [
                {
                    "type": "node",
                    "data": {
                        "uin": (await bot.get_login_info())["user_id"],
                        "name": (await bot.get_login_info())["nickname"],
                        "content": _lang.text("who_at_me.info", [
                            (await bot.get_group_info(group_id=item["group_id"]))["group_name"],
                            item["group_id"],
                            time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(item["time"]))
                        ], event.get_user_id())
                    }
                }
            ]
            for message in item["messages"]:
                message_data = (await bot.get_msg(message_id=message))
                sub_node.append({
                    "type": "node",
                    "data": {
                        "uin": message_data["sender"]["user_id"],
                        "name": message_data["sender"]["nickname"],
                        "time": message_data["time"],
                        "content": str(message_data["message"]).replace(
                            f"[CQ:at,qq={event.user_id}]",
                            f"[[@{(await bot.get_stranger_info(user_id=event.user_id))['nickname']}]] "
                        )
                    }
                })
            node_messages.append({
                "type": "node",
                "data": {
                    "uin": item["user_id"],
                    "name": (await bot.get_stranger_info(user_id=item["user_id"]))["nickname"],
                    "content": sub_node
                }
            })
        await bot.call_api(
            "send_group_forward_msg",
            group_id=event.group_id,
            messages=node_messages
        )
        Json("who_at_me.data.json")[str(event.user_id)] = []
    except:
        await _error.report()
"""