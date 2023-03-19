from nonebot import on_command
from nonebot.adapters.onebot.v11.event import MessageEvent
# from nonebot.adapters.onebot.v11.bot import Bot
from nonebot.adapters.onebot.v11 import Message
from nonebot.params import CommandArg
from .etm import bag
# from . import _lang as lang
from . import _error as error
import traceback

use_cmd = on_command("use", aliases={"使用"})

@use_cmd.handle()
async def use_item(event: MessageEvent, message: Message = CommandArg()):
    try:
        qq = event.get_user_id()
        await use_cmd.finish(bag.use_item(
            qq, int(message.extract_plain_text().split(" ")[0]), 
            " ".join(message.extract_plain_text().split(" ")[1:])))

    except BaseException:
        await error.report(traceback.format_exc(), use_cmd)
