from time import time
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message
from nonebot import on_message
import json
from . import _lang
from . import _error
from . import _userCtrl
from nonebot.exceptions import FinishedException
import random
import traceback

random_give = on_message()
latest = time()


@random_give.handle()
async def random_give_handle(event: GroupMessageEvent):
    global latest
    try:
        if event.group_id in json.load(open("data/random_events.disable.json"))["random_give"]:
            await random_give.finish()
        if time() - latest >= 600 and random.random() <= 0.15:
            reply = _lang.text(
                "random_give.reply",
                [f"[CQ:at,qq={event.get_user_id()}]"],
                event.get_user_id())
            send_reply = False
            length = 1

            if random.random() <= 0.10:
                add_coin = random.randint(5, 20)
                _userCtrl.addItem(event.get_user_id(), "0", add_coin, {})
                reply += f"\n {length}. VimCoin x{add_coin}"
                send_reply = True
                length += 1
            if random.random() <= 0.07:
                add_exp = random.randint(15, 20)
                _userCtrl.addExp(event.get_user_id(), add_exp)
                reply += f"\n {length}. 经验 x{add_exp}"
                send_reply = True
                length += 1
            else:
                _userCtrl.addExp(event.get_user_id(), random.randint(0, 10))
            if random.random() <= 0.05:
                add_role = random.randint(1, 2)
                _userCtrl.addItem(event.get_user_id(), "3", add_role, {})
                reply += f"\n {length}. 二十面骰 x{add_role}"
                send_reply = True
                length += 1

            if send_reply:
                await random_give.send(Message(reply))
            latest = time()

        else:
            if random.random() <= 0.2:
                _userCtrl.addExp(event.get_user_id(), random.randint(1, 2))
    except FinishedException:
        raise FinishedException()
    except BaseException:
        await _error.report(traceback.format_exc())
