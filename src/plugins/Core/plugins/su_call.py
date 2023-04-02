import json
from nonebot.adapters.onebot.v11 import Bot
from nonebot.params import CommandArg
from .su import su
from . import _error
import traceback


@su.handle()
async def call_api(bot: Bot, argument: list = str(CommandArg()).split(" ")):
    try:
        if argument[0] in ["call", "调用"]:
            await su.finish(
                json.dumps(
                    await bot.call_api(
                        api=argument[1],
                        data=json.loads(" ".join(argument[2:])))))

    except BaseException:
        await _error.report(traceback.format_exc(), su)
