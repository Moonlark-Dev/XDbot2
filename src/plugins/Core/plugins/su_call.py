import json
from nonebot.adapters.onebot.v11 import Bot
from nonebot.adapters.onebot.v11 import Message
from nonebot.params import CommandArg
from .su import su
from . import _error
import traceback


@su.handle()
async def call_api(bot: Bot, message: Message = CommandArg()):
    argument = str(message).split(" ")
    try:
        if argument[0] in ["call", "调用"]:
            await su.finish(
                json.dumps(
                    await bot.call_api(
                        api=argument[1],
                        **json.loads(" ".join(argument[2:])))))

    except BaseException:
        await _error.report(traceback.format_exc(), su)
