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
                item = items.json2items([item_dict])[0]
                reply += f"\n{item_id}. {item.data['display_name']} {economy.vi2vim(item.data['price'])}vim"
            await shop.finish(reply)
        elif arguments[0] == "view":
            item = items.json2items([SHOP_ITEMS[arguments[1]]])[0]
            reply = f"「商品信息（#{arguments[1]}）」\n{'-'*30}\n"
            reply += f"物品：{item.data['display_name']} {item.item_id}"
            reply += f"价格：{economy.vi2vim(item.data['price'])}vim ({item.data['price']}vi)"
            reply += f"简介：{item.data['information']}"
                

    except BaseException:
        await error.report(traceback.format_exc(), shop)

