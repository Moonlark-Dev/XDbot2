import json
import traceback
from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, Message
from nonebot.exception import FinishedException
from nonebot.params import CommandArg
from . import _error
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
        if len(argument) == 1:
            await use.finish(
                Message(_userCtrl.useItem(event.get_user_id(), int(argument[0])))
            )
        elif len(argument) == 2:
            node_msg = []
            user_info = await bot.get_login_info()
            for _ in range(int(argument[1])):
                try:
                    node_msg.append({
                        "type": "node",
                        "data": {
                            "uin": str(user_info["user_id"]),
                            "name": user_info["nickname"],
                            "content": _userCtrl.useItem(event.get_user_id(), int(argument[0]))
                        }
                    })
                except _userCtrl.NotHaveEnoughItem:
                    await use.send(_lang.text("use.notenough", [], event.get_user_id()))
                    break
                except BaseException:
                    await _error.report(traceback.format_exc())
                    break
            await bot.call_api(
                api="send_group_forward_msg",
                messages=node_msg,
                group_id=str(event.group_id))
    except _userCtrl.ItemCanNotRemove:
        await use.finish(_lang.text("use.cannot", [], event.get_user_id()))
    except FinishedException:
        raise FinishedException()
    except _userCtrl.NotHaveEnoughItem:
        await use.finish(_lang.text("use.notenough", [], event.get_user_id()))
    except IndexError:
        await use.finish(_lang.text("use.notfound", [], event.get_user_id()))
    except BaseException:
        await _error.report(traceback.format_exc())


# [HELPSTART]
# !Usage 1 use <背包物品ID> [数量]
# !Info 1 使用物品
# [HELPEND]
