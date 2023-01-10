import traceback
from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, Message
from nonebot.exception import FinishedException
from nonebot.params import CommandArg
from . import _userCtrl
import json

use = on_command("use", aliases={"使用"})
ctrlGroup = json.load(open("data/ctrl.json", encoding="utf-8"))["control"]


@use.handle()
async def useHandle(
        bot: Bot,
        event: GroupMessageEvent,
        message: Message = CommandArg()):
    try:
        argument = int(message.extract_plain_text())
        await use.finish(Message(
            _userCtrl.useItem(
                event.get_user_id(), argument)))

    except _userCtrl.ItemCanNotRemove:
        await use.finish("物品被标记为：不可使用")
    except FinishedException:
        raise FinishedException()
    except Exception:
        await bot.send_group_msg(
            message=traceback.format_exc(),
            group_id=ctrlGroup
        )
        await use.finish("处理失败")
