import json
import traceback
from . import _error
from . import _lang
from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, Message
from nonebot.exception import FinishedException
from nonebot.params import CommandArg

# from psutil import users
from . import _userCtrl

ctrlGroup = json.load(open("data/ctrl.json", encoding="utf-8"))["control"]
shop = on_command("shop", aliases={"商店"})


@shop.handle()
async def shopHandle(
        bot: Bot,
        event: GroupMessageEvent,
        message: Message = CommandArg()):
    try:
        shopData = json.load(open("data/shop.items.json", encoding="utf-8"))
        argument = message.extract_plain_text().split(" ")
        if argument[0] == "":
            text = _lang.text("shop.name",[],event.get_user_id())
            for item in list(shopData.keys()):
                text += f"{item}. {shopData[item]['name']} ({shopData[item]['price']} vi)\n"
            await shop.finish(Message(text))
        elif argument[0] == "view" or argument[0] == "查看":
            item = shopData[argument[1]]
            text = f"""+-----「{_lang.text('shop.info_title',[],event.get_user_id())}」-----+
\t「{item['name']}」
  {_lang.text('shop.info_num',[],event.get_user_id())}{item['count']}
  {_lang.text('shop.info_price',[],event.get_user_id())}{item['price']} vi
  {_lang.text('shop.info_seller',[],event.get_user_id())}{item['seller']['nickname']}({item['seller']['user_id']})
  -----------------------
  {item['info']}
+-------------------------+"""
            await shop.finish(Message(text))
        elif argument[0] == "buy" or argument[0] == "购买":
            shopData = json.load(
                open(
                    "data/shop.items.json",
                    encoding="utf-8"))
            itemData = shopData[argument[1]]
            try:
                count = int(argument[2])
            except IndexError:
                count = 1
            # 检查是否符合购买条件
            if _userCtrl.getCountOfItem(
                    event.get_user_id(), "0") < itemData["price"]:
                await shop.finish(_lang.text("shop.poor",[],event.get_user_id()), at_sender=True)
            if "maxBuy" in list(itemData.keys()):
                if "bought" in list(itemData.keys()):
                    if event.get_user_id() in list(itemData["bought"].keys()):
                        if itemData["bought"][event.get_user_id()
                                              ] >= itemData["maxBuy"]:
                            await shop.finish(_lang.text("shop.out_of_max",[itemData["maxBuy"]],event.get_user_id()), at_sender=True)
                        else:
                            itemData["bought"][event.get_user_id()] += 1
                    else:
                        itemData["bought"][event.get_user_id()] = 1
            if count > itemData["count"]:
                await shop.finish(_lang.text("shop.not_enough",[],event.get_user_id()), at_sender=True)
            # 购买
            if _userCtrl.removeItemsByID(
                    event.get_user_id(), "0", itemData["price"] * count):
                _userCtrl.addItem(
                    event.get_user_id(),
                    itemData["item"]["id"],
                    count,
                    itemData["item"])
                _userCtrl.addItem(
                    itemData["seller"]["user_id"],
                    "0",
                    itemData["price"] *
                    count,
                    {})
                _userCtrl.addExp(event.get_user_id(), int(count / 2))
                # 修改商店数据
                if count == itemData["count"]:
                    shopData.pop(argument[1])
                else:
                    shopData[argument[1]]["count"] -= count
                # 保存数据
                json.dump(
                    shopData,
                    open(
                        "data/shop.items.json",
                        "w",
                        encoding="utf-8"))
                await shop.finish(_lang.text("shop.buy_success",[],event.get_user_id()), at_sender=True)
            else:
                await shop.finish(_lang.text("shop.buy_failed",[],event.get_user_id()), at_sender=True)

        elif argument[0] == "sell" or argument[0] == "卖出":
            bagData = json.load(open("data/etm.bag.json", encoding="utf-8"))
            items = json.load(open("data/etm.items.json", encoding="utf-8"))
            item = bagData[event.get_user_id()][int(argument[1])]
            item["count"] = 1
            try:
                _userCtrl.removeItemsFromBag(
                    event.get_user_id(),
                    int(argument[1]),
                    int(argument[2]),
                    "Sell"
                )
            except _userCtrl.NotHaveEnoughItem:
                await shop.finish(_lang.text("shop.sell_not_enough",[],event.get_user_id()))
            except _userCtrl.ItemCanNotRemove:
                await shop.finish(_lang.text("shop.sell_cannot_remove",[],event.get_user_id()))
            itemData = {
                "name": item["data"]["displayName"] or items[item["id"]]["name"],
                "info": item["data"]["information"] or items[item["id"]]["info"],
                "price": int(argument[3]),
                "count": int(argument[2]),
                "item": item,
                "seller": await bot.get_stranger_info(user_id=event.get_user_id())
            }
            shopData = json.load(
                open(
                    "data/shop.items.json",
                    encoding="utf-8"))
            itemIDs = shopData.keys()
            length = 0
            while True:
                if str(length) not in itemIDs:
                    shopData[str(length)] = itemData
                    break
                length += 1
            json.dump(shopData, open(
                "data/shop.items.json", "w", encoding="utf-8"))
            await bot.send_group_msg(
                message=_lang.text("shop.sell_success1",[length,itemData],event.get_user_id()),
                group_id=ctrlGroup)
            await shop.finish(_lang.text("shop.sell_success2",[length],event.get_user_id()), at_sender=True)

    except FinishedException:
        raise FinishedException()
    except KeyError:
        await shop.finish(_lang.text("shop.key_error",[],event.get_user_id()))
    except Exception:
        await _error.report(traceback.format_exc(), shop)

# [HELPSTART] Version: 2
# Command: shop
# Info: XDbot2 娱乐系统道具商城操作
# Msg: 道具商城
# Usage: shop：查看商品列表
# Usage: shop view <商品ID>：查看商品详情
# Usage: shop buy <商品ID> <数量>：购买商品
# Usage: shop sell <背包物品ID> <数量> <标价>：出售商品
# [HELPEND]
