from nonebot import on_command
from nonebot.adapters.onebot.v11 import Message, MessageEvent
from .etm import exp, economy, bag, items, user
from nonebot.params import CommandArg
from . import _lang as lang
from . import _error as error
import json
import traceback
from .etm import mystery_box

shop = on_command("shop", aliases={"系统商店", "systemshop", "ss"})
SHOP_ITEMS = {
    "1": {"id": "dice", "count": 1, "data": {}},
    # "2": {"id": "book_and_quill", "count": 1, "data": {}},
    "2": {"id": "talisman", "count": 1, "data": {}},
    # "4": {"id": "pouch", "count": 1, "data": {}},
    "3": {"id": "mysterious_shard", "count": 1, "data": {}},
    # "3": {"id": "towel.zip", "count": 1, "data": {}},
    "4": {"id": "mysterybox_lv1", "count": 1, "data": {}},
    "5": {"id": "pawcoin", "count": 1, "data": {}},
}
mystery_box.SHOP_ITEMS = SHOP_ITEMS


@shop.handle()
async def shop_handler(event: MessageEvent, message: Message = CommandArg()):
    try:
        arguments = message.extract_plain_text().split(" ")
        qq = event.get_user_id()
        if arguments[0] == "":
            reply = f"「系统商店」\n——————————————"
            for item_id, item_dict in list(SHOP_ITEMS.items()):
                item = items.json2items([item_dict])[0]
                reply += f"\n{item_id}. {item.data['display_name']} {economy.vi2vim(item.data['price'])}vim"
            await shop.finish(reply)
        elif arguments[0] == "view":
            item = items.json2items([SHOP_ITEMS[arguments[1]]])[0]
            await shop.finish(
                (
                    f"「商品信息（#{arguments[1]}）」\n"
                    "——————————————\n"
                    f"物品：{item.data['display_name']} ({item.item_id})\n"
                    f"价格：{economy.vi2vim(item.data['price'])}vim (可购：{int(user.get_user_data(qq)['vimcoin'] / item.data['price'])})\n"
                    f"简介：\n  {item.data['display_message']}"
                )
            )
        elif arguments[0] == "buy":
            item = items.json2items([SHOP_ITEMS[arguments[1]]])[0]
            if len(arguments) >= 3:
                count = min(int(arguments[2]), int(item.data["maximum_stack"]))
            else:
                count = 1
            if economy.use_vi(qq, item.data["price"] * count)[0]:
                exp.add_exp(qq, int(1 * (1 + count / 25)))
                bag.add_item(qq, item.item_id, count, item.data)
                await shop.finish("购买成功！\n使用「/bag」查看", at_sender=True)
            else:
                await shop.finish("失败：余额不足！", at_sender=True)

    except BaseException:
        await error.report(traceback.format_exc(), shop)
