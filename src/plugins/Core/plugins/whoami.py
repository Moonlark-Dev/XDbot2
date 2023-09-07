from ._utils import *

# from nonebot import on_command
from nonebot.adapters.onebot.v11 import MessageEvent

# , GroupMessageEvent, PrivateMessageEvent, MessageSegment


@create_command("whoami")
async def _(_bot, event: MessageEvent, _message):
    await finish(
        "whoami.text",
        [event.sender.user_id, event.sender.nickname],
        event.sender.user_id,
        False,
        True,
    )


# [HELPSTART] Version: 2
# Command: whoami
# Info: 获取用户信息。
# Msg: 我是谁？
# Usage: whoami: 获取使用用户的信息
# [HELPEND]
