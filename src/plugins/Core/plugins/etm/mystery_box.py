import traceback
from .economy import IllegalQuantityException
from . import bag
from src.plugins.Core.plugins import _lang
import random
from .item import Item
from .nbt import NbtDict


def json2items(items, user_id=None):
    ...


SHOP_ITEMS = {}


class MysteryBoxLevel1(Item):
    def on_register(self):
        self.basic_data: NbtDict = {
            "display_name": "Mystery Box (⭐️)",
            "display_message": ("并不普通的的盒子，散发着少许神秘的气息。\n \n「盒子里好像……发光了？」"),
            "price": 32,
        }
        self.item_id = "mysterybox_lv1"

    def use_item(self):
        items = []
        # 普通物品
        items.append({"id": "vimcoin", "count": random.randint(15, 60), "data": {}})
        items.append({"id": "exp", "count": random.randint(1, 30), "data": {}})
        # 商店物品
        for _ in range(random.randint(0, 5)):
            item: Item = json2items([random.choice(list(SHOP_ITEMS.values()))])[0]
            items.append(
                {
                    "id": item.item_id,
                    "count": random.randint(
                        1,
                        min(
                            item.data["maximum_stack"],
                            max(1, int(32 / item.data["price"])),
                        ),
                    ),
                    "data": {},
                }
            )
        # 大紫（确信
        if random.random() <= 0.15:
            items.append(
                {"id": "auto_sign_coupon", "count": random.randint(1, 5), "data": {}}
            )
        if random.random() <= 0.12:
            items.append({"id": "talisman", "count": 1, "data": {}})
        if random.random() <= 0.17:
            items.append({"id": "pawcoin", "count": random.randint(1, 7), "data": {}})
        if random.random() <= 0.75:
            items.append(
                {"id": "mysterious_shard", "count": random.randint(1, 25), "data": {}}
            )

        items = json2items(items)
        if not self.length:
            self.length = 1
            reply_text = " " + _lang.text("mystery_box.get", [], self.user_id)
        else:
            reply_text = ""
        for item in items:
            bag.add_item(self.user_id, item.item_id, item.count, item.data)
            reply_text += f"\n{self.length}. {item.data['display_name']} x{item.count}"
            self.length += 1
        return reply_text[1:]

    def use(self, args):
        if not self.data["useable"]:
            return ["失败：物品无法被使用"]

        try:
            count = int(args)
        except BaseException:
            count = 1

        if count <= 0 or count >= 200:
            raise IllegalQuantityException(count)
        self.length = 0
        msg = []
        if self.count >= count:
            for _ in range(count):
                try:
                    msg.append(self.use_item())
                except BaseException:
                    msg.append(f"发生错误：{traceback.format_exc()}")
            self.count -= count
        else:
            msg = [f"错误：数量不足（拥有 {self.count} 个）"]
        return msg


class MysteriousShard(Item):
    def on_register(self):
        self.item_id = "mysterious_shard"
        self.basic_data: NbtDict = {
            "display_name": "神秘碎片",
            "display_message": "………………\n \n「……」",
            "price": 2,
            "useable": False,
        }
