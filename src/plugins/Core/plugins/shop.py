import json
import traceback
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
            text = "XDbot2 道具商城：\n"
            for item in list(shopData.keys()):
                text += f"{item}. {shopData[item]['name']} ({shopData[item]['price']} vi)\n"
            await shop.finish(Message(text))
        elif argument[0] == "view" or argument[0] == "查看":
            item = shopData[argument[1]]
            text = f"""+-----「商品信息」-----+
\t「{item['name']}」
  存货量：{item['count']}
  售价：{item['price']} vi
  卖家：{item['seller']['nickname']}({item['seller']['user_id']})
  -----------------------
  {item['info']}
+-------------------------+"""
            await shop.finish(Message(text))
        elif argument[0] == "buy" or argument[0] == "购买":
            shopData = json.load(open("data/shop.items.json", encoding="utf-8"))
            itemData = shopData[argument[1]]
            try:
                count = int(argument[2])
            except IndexError:
                count = 1
            # 检查是否符合购买条件
            if _userCtrl.getCountOfItem(event.get_user_id(), "0") < itemData["price"]:
                await shop.finish("余额不足！", at_sender = True)
            if "maxBuy" in list(itemData.keys()):
                if "bought" in list(itemData.keys()):
                    if event.get_user_id() in list(itemData["bought"].keys()):
                        if itemData["bought"][event.get_user_id()] >= itemData["maxBuy"]:
                            await shop.finish(f"商品被标记为：最多购买 {itemData['maxBuy']} 次", at_sender=True)
                        else:
                            itemData["bought"][event.get_user_id()] += 1
                    else:
                        itemData["bought"][event.get_user_id()] = 1
            if count > itemData["count"]:
                await shop.finish("库存不足！", at_sender=True)
            # 购买
            if _userCtrl.removeItemsByID(event.get_user_id(), "0", itemData["price"] * count):
                _userCtrl.addItem(event.get_user_id(), itemData["item"]["id"], count, itemData["item"])
                _userCtrl.addItem(itemData["seller"]["user_id"], "0", itemData["price"] * count, {})
                _userCtrl.addExp(event.get_user_id(), int(count / 2))
                # 修改商店数据
                if count == itemData["count"]:
                    shopData.pop(argument[1])
                else:
                    shopData[argument[1]]["count"] -= count
                # 保存数据
                json.dump(shopData, open("data/shop.items.json", "w", encoding="utf-8"))
                await shop.finish("购买成功！", at_sender=True)
            else:
                await shop.finish("余额不足！", at_sender = True)

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
                await shop.finish("物品数量不足")
            except _userCtrl.ItemCanNotRemove:
                await shop.finish("物品被标记为：不可出售")
            itemData = {
                "name": item["data"]["displayName"] or items[item["id"]]["name"],
                "info": item["data"]["information"] or items[item["id"]]["info"],
                "price": int(argument[3]),
                "count": int(argument[2]),
                "item": item,
                "seller": await bot.get_stranger_info(user_id=event.get_user_id())
            }
            shopData = json.load(open("data/shop.items.json", encoding="utf-8"))
            itemIDs = shopData.keys()
            length = 0
            while True:
                if str(length) not in itemIDs:
                    shopData[str(length)] = itemData
                    break
                length += 1
            json.dump(shopData, open("data/shop.items.json", "w", encoding="utf-8"))
            await bot.send_group_msg(
                message=f"「道具商店新上架（#{length}）」\n{itemData}",
                group_id=ctrlGroup)
            await shop.finish(f"上架成功，ID：#{length}", at_sender=True)


    except FinishedException:
        raise FinishedException()
    except Exception:
        await bot.send_group_msg(
            message=traceback.format_exc(),
            group_id=ctrlGroup
        )
        await shop.finish("处理失败")
    
