from nonebot import on_command
from nonebot.adapters.onebot.v11 import Message, MessageEvent
from .etm import exp, economy, bag, items
from nonebot.params import CommandArg

from . import _lang as lang
from . import _error as error
import json
import traceback

shop = on_command("shop", aliases={"系统商店", "systemshop", "ss"})
SHOP_ITEMS = {
    "1": {
        "id": "dice",
        "count": 1,
        "data": {}
    }
}


@shop.handle()
async def shop_handler(event: MessageEvent, message: Message = CommandArg()):
    try:
        arguments = message.extract_plain_text().split(" ")
        qq = event.get_user_id()
        if arguments[0] == "":
            reply = f"「系统商店」\n{'-'*30}"
            for item_id, item_dict in list(SHOP_ITEMS.items()):
                item = items.json2items(item_dict)[0]
                reply += f"{item_id}. {item.data['display_name']} {economy.vi2vim(item.data['price'])}vim"
            await shop.finish(reply)
                

    except BaseException:
        await error.report(traceback.format_exc(), shop)

