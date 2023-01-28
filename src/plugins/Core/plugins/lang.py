from nonebot import on_command
from nonebot.adapters.onebot.v11 import (Bot, Message, MessageEvent)
from nonebot.params import CommandArg
from . import _lang
import json,os
lang = on_command("lang", aliases={"语言"})
@lang.handle()
async def lang_handle(bot: Bot,
                       event: MessageEvent,
                       message: Message = CommandArg()):
    args = message.extract_plain_text()
    if args == "":
        await lang.finish(_lang.text("lang.empty",["/lang <lang>"],event.get_user_id()))
    else:
        if os.path.exists(f"src/plugins/Core/lang/{args}.json") or args == "debug":
            with open("data/lang.users.json", "r") as f:
                _lang_user = json.load(f)
            _lang_user[event.get_user_id()] = args
            with open("data/lang.users.json", "w") as f:
                json.dump(_lang_user, f)
            await lang.finish(_lang.text("lang.success",[args],event.get_user_id()))
        else:
            await lang.finish(_lang.text("lang.notfound",[args],event.get_user_id()))