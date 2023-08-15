from nonebot import on_command, on_regex
from . import _error as error
from nonebot.adapters.onebot.v11.event import MessageEvent
from . import _lang as lang
from .etm import economy, exp, user, achievement
import traceback

pay = on_command("pay", aliases={"转账"})

# [HELPSTART] Version: 2
# Command: pay
# Usage: pay <QQ号> <金额>
# Info: 给别人转账
# [HELPEND]


@pay.handle()
async def pay(bot: Bot, event: GroupMessageEvent, message: Message = CommandArg())):
    try:
        argument = str(message).split(" ")
        qq = argument[0]
        num = float(argument[1])
        src_qq = event.get_user_id()
        data = user.get_user_data(src_qq)
        vim_src = data["vimcoin"]
        if num > eco_src:
            await pay.finish(lang.text("pay.vim_not_enough", [], src_qq))
        economy.add_vi(src_qq, -num)
        economy.add_vi(qq, num)
        await pay.finish(lang.text("pay.sucess", [], src_qq))
    except BaseException:
        await _error.report(traceback.format_exc(), pay)
