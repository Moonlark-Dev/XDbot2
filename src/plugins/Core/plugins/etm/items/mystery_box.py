import traceback
from ..illegal_quantity import IllegalQuantityException
from .. import bag
from src.plugins.Core.plugins import _lang
import random
from ..item import Item
from ..nbt import NbtDict


def json2items(items, user_id=None): ...


class MysteryBoxLevel1(Item):
    def on_register(self):
        self.basic_data = {
            "display_name": "Mystery Box (⭐️)",
            "display_message": (
                "并不普通的的盒子，散发着少许神秘的气息。\n \n「盒子里好像……发光了？」"
            ),
            "price": 35,
        }
        self.item_id = "mysterybox_lv1"

    def use_item(self):
        items = []
        for _ in range(random.randint(3, 5)):
            items.append(
                {
                    "id": (item := random.choice(self.get_items()["ordinary"]))[
                        "item_id"
                    ],
                    "count": random.randint(item["count"][0], item["count"][1]),
                    "data": item.get("data", {}),
                }
            )
        for _ in range(random.randint(2, 3)):
            items.append(
                {
                    "id": (item := random.choice(self.get_items()["rare"]))["item_id"],
                    "count": random.randint(item["count"][0], item["count"][1]),
                    "data": item.get("data", {}),
                }
            )
        if random.random() <= 0.25:
            items.append(
                {
                    "id": (item := random.choice(self.get_items()["rare"]))["item_id"],
                    "count": random.randint(item["count"][0], item["count"][1]),
                    "data": item.get("data", {}),
                }
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

    def get_items(self):
        return {
            "ordinary": [
                {"item_id": "dice", "count": [1, 16]},
                {"item_id": "mysterious_shard", "count": [1, 15]},
                {"item_id": "pawcoin", "count": [1, 10]},
                {"item_id": "common_rubbish", "count": [1, 10]},
            ],
            "rare": [
                {"item_id": "vimcoin", "count": [1, 40]},
                {"item_id": "auto_sign_coupon", "count": [1, 5]},
                {"item_id": "talisman", "count": [1, 2]},
                {"item_id": "archfiend_dice", "count": [1, 1]},
            ],
            "legend": [
                {"item_id": "mysterybox_lv1", "count": [1, 1]},
                {"item_id": "gpt_monthly_pass", "count": [1, 1]},
            ],
        }

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
                    print(f"发生错误：{traceback.format_exc()}")
                    msg.append(f"发生错误：{traceback.format_exc()}")
            self.count -= count
        else:
            msg = [f"错误：数量不足（拥有 {self.count} 个）"]
        return msg


class MysteryBoxLv3(MysteryBoxLevel1):
    def on_register(self):
        super().on_register()
        self.item_id = "mysterybox_lv3"
        self.basic_data["price"] = 64
        self.basic_data["display_message"] = (
            "并不普通的的盒子，散发着一些神秘的气息。\n \n「盒子里好像……发光了？」"
        )
        self.basic_data["display_name"] = "Mystery Box (⭐️⭐️⭐️)"

    def get_items(self):
        return {
            "ordinary": [
                {"item_id": "dice", "count": [5, 16]},
                {"item_id": "mysterious_shard", "count": [5, 30]},
                {"item_id": "pawcoin", "count": [2, 15]},
                {"item_id": "towel", "count": [1, 16]},
                {"item_id": "book_and_quill", "count": [1, 1]},
                {"item_id": "pouch", "count": [1, 1]},
                {"item_id": "vimcoin", "count": [5, 20]},
                {"item_id": "mysterious_shard", "count": [10, 35]},
                {"item_id": "towel.zip", "count": [1, 5]},
                {"item_id": "auto_sign_coupon", "count": [1, 5]},
                {
                    "item_id": "weapons",
                    "count": [1, 1],
                    "data": {"kit": "leather_case"},
                },
                {"item_id": "ball", "count": [1, 1], "data": {"kit": "leather_case"}},
            ],
            "rare": [
                {"item_id": "mysterybox_lv1", "count": [1, 2]},
                {"item_id": "talisman", "count": [1, 4]},
                {"item_id": "vimcoin", "count": [20, 60]},
                {
                    "item_id": "weapons",
                    "count": [1, 1],
                    "data": {"kit": "scrorching_sun_phantom"},
                },
            ],
            "legend": [
                {"item_id": "mysterybox_lv3", "count": [1, 2]},
                {"item_id": "weapons", "count": [1, 1], "data": {"kit": "ice_king"}},
                {"item_id": "ball", "count": [1, 1], "data": {"kit": "ice_king"}},
                {
                    "item_id": "ball",
                    "count": [1, 1],
                    "data": {"kit": "scrorching_sun_phantom"},
                },
            ],
        }


class MysteriousShard(Item):
    def on_register(self):
        self.item_id = "mysterious_shard"
        self.basic_data: NbtDict = {
            "display_name": "神秘碎片",
            "display_message": "………………\n \n「……」",
            "price": 1,
            "useable": False,
        }
