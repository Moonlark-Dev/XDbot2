from nonebot import on_command
from ._utils import *
from . import _lang as lang
from .etm import economy, user
import traceback

pay = on_command("pay", aliases={"转账"})

# [HELPSTART] Version: 2
# Command: pay
# Usage: pay <QQ号> <金额>
# Info: 给别人转账
# [HELPEND]


@pay.handle()
async def handle_pay_command(event: MessageEvent, message: Message = CommandArg()):
    try:
        argument = str(message).split(" ")
        qq = int(argument[0].replace("[CQ:at,qq=", "").replace("]", ""))
        num = float(argument[1])
        src_qq = event.get_user_id()
        if not economy.use_vimcoin(src_qq, num):
            await pay.finish(lang.text("pay.vim_not_enough", [], src_qq))
        economy.add_vi(qq, num)
        await pay.finish(lang.text("pay.sucess", [], src_qq))
    except ValueError:
        await pay.finish(lang.text("pay.failed", [], event.user_id))
    except BaseException:
        await error.report(traceback.format_exc())
