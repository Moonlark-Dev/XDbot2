from nonebot.adapters.onebot.v11 import Message
from nonebot.params import CommandArg
from .su import su
from traceback import format_exc
from . import _error as error
from nonebot.adapters.onebot.v11 import Message


@su.handle()
async def echo(message: Message = CommandArg()):
    argument = str(message).split(" ")
    try:
        if argument[0] in ["echo", "调试输出"]:
            await su.send(
                Message(
                    ("".join(argument[1:]).replace(
                        "&#91;", "[").replace("&#93;", "]"))
                )
            )
    except BaseException:
        await error.report(format_exc(), su)
