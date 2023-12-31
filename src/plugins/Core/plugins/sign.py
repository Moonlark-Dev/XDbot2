from nonebot import on_command, on_regex

from ._sign import _sign
from . import _error as error
from nonebot.adapters.onebot.v11.event import MessageEvent
import traceback


sign = on_regex("^(签到|.sign)$")
sign_rank = on_command("sign-rank")


@sign.handle()
async def sign_handler(event: MessageEvent):
    try:
        await sign.finish(_sign(event.get_user_id()))
    except BaseException:
        await error.report(traceback.format_exc(), sign)
