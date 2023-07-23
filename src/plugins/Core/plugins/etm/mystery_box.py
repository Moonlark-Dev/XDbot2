from . import bag
import random
from .item import Item
from src.plugins.Core.plugins.shop import SHOP_ITEMS
from .nbt import NbtDict

json2items = None

class MysteryBoxLevel1(Item):

    def on_register(self):
        self.basic_data: NbtDict = {
            "display_name": "Mystery Box (⭐️)",
            "display_message": (
                "十分神秘的盒子，没人知道它为什么会出现在这里，也没人知道里面有什么\n\n"
                "「盒子里好像……发光了？」"
            ),
            "price": 32
        }
        self.item_id = "mysterybox_lv1"

    def use_item(self):
        items = []
        # 普通物品
        items.append({
            "id": "vimcoin",
            "count": random.randint(30, 60),
            "data": {}
        })
        items.append({
            "id": "exp",
            "count": random.randint(1, 50),
            "data": {}
        })
        # 商店物品
        for _ in range(random.randint(1, 5)):
            item: Item = json2items([random.choice(SHOP_ITEMS)])[0]
            items.append({
                "id": item.item_id,
                "count": random.randint(1, max(2, int(64 / item.data["price"]))),
                "data": {}
            })

        items = json2items(items)
        length = 1
        reply_text = "你获得了："
        for item in items:
            bag.add_item(self.user_id, item.item_id, item.count, item.data)
            reply_text += f"\n{length}. {item.data['display_name']} x{item.count}"
        return reply_text
