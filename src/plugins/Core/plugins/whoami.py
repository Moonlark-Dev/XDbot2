from _utils import *
from nonebot import on_command
from nonebot.adapters.onebot.v11 import MessageEvent, GroupMessageEvent, PrivateMessageEvent, MessageSegment

@create_command("whoami")
async def _(event: MessageEvent):
    await finish("whoami.text", [event.sender.user_id, event.sender.nickname], event.sender.user_id, False, True)

# [HELPSTART] Version: 2
# Command: whoami
# Info: 我是谁？
# Msg: 我是谁
# Usage: whoami: 我是谁？
# [HELPEND]
