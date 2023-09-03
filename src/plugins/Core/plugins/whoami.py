from _utils import *
from nonebot import on_command
from nonebot.adapters.onebot.v11 import MessageEvent, GroupMessageEvent, PrivateMessageEvent, MessageSegment

@create_command("whoami")
async def _(event: MessageEvent):
    await finish(MessageSegment.reply(event.message_id) + MessageSegment.text(f"{event.sender.nickname}"))

# [HELPSTART] Version: 2
# Command: whoami
# Info: 我是谁？
# Msg: 我是谁
# Usage: whoami: 我是谁？
# [HELPEND]
