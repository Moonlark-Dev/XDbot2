from nonebot import on_regex
from nonebot import on_command
from . import _error as error
from nonebot.adapters.onebot.v11.event import MessageEvent
from . import _lang as lang
from .etm import economy
import traceback
import time

get_exchange_rate = on_command("getexchangerate", aliases={"ger","获取当前汇率", "获取汇率"})

@get_exchange_rate.handle()
async def handler(event: MessageEvent):
    try:
        qq = event.get_user_id()
        await get_exchange_rate.send("\n".join((
            lang.text("ger.title", [time.strftime("%H:%M:%S", time.localtime())], qq),
            lang.text("ger.io", [economy.vimcoin["in"], economy.vimcoin["out"]], qq),
            lang.text("ger.er", [economy.vi2vim(1)], qq)
        )))



    except BaseException:
        await error.report(traceback.format_exc(), get_exchange_rate
