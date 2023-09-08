from ._utils import *

from nonebot.adapters.onebot.v11 import MessageEvent, Message
from nonebot.params import CommandArg
from nonebot import get_driver


@create_command("whoami")
async def _(_bot, event: MessageEvent, message: Message = CommandArg()):
    args = str(message).split(" ")
    if args[0] == "" or len(args) == 0:
        await finish(
            "whoami.text",
            [event.sender.user_id, event.sender.nickname],
            event.sender.user_id,
            False,
            True,
        )
    elif args[0] == "detail":
        await finish(
            "whoami.text.detail",
            [event.sender.user_id, event.sender.nickname, event.sender.sex, event.sender.age, event.sender.level, event.sender.role, event.sender.title],
            event.sender.user_id,
            False,
            True,
        )
    else:
        await finish(
            "whoami.findhelp",
            [],
            event.sender.user_id,
            False,
            True,
        )

# [HELPSTART] Version: 2
# Command: whoami
# Info: 获取用户信息。
# Msg: 我是谁？
# Usage: whoami: 获取使用用户的信息。
# [HELPEND]
