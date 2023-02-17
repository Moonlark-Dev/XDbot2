import json
import traceback

from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, Message
from nonebot.exception import FinishedException
from nonebot.params import CommandArg

from . import _userCtrl
from . import _lang

use = on_command("use", aliases={"使用"})
ctrlGroup = json.load(open("data/ctrl.json", encoding="utf-8"))["control"]


@use.handle()
async def useHandle(
    bot: Bot, event: GroupMessageEvent, message: Message = CommandArg()
):
    try:
        argument = message.extract_plain_text().split(" ")
        if len(argument)==1:
            await use.finish(
                Message(_userCtrl.useItem(event.get_user_id(), int(argument[0]))), at_sender=True
            )
        elif len(argument)==2:
            for i in range(int(argument[1])):
                await use.finish(
                    Message(_userCtrl.useItem(event.get_user_id(), int(argument[0]))), at_sender=True
                )

    except _userCtrl.ItemCanNotRemove:
        await use.finish(_lang.text("use.cannot", [], event.get_user_id()))
    except FinishedException:
        raise FinishedException()
    except IndexError:
        await use.finish(_lang.text("use.notfound", [], event.get_user_id()))
    except Exception:
        await bot.send_group_msg(message=traceback.format_exc(), group_id=ctrlGroup)
        await use.finish(_lang.text("use.error", [], event.get_user_id()))


# [HELPSTART]
# !Usage 1 use <背包物品ID>
# !Info 1 使用物品
# [HELPEND]
