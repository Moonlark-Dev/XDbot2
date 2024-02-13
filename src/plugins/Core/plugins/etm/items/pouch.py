from typing import Optional
from ..exception import IllegalQuantityException
from ..item import Item
from .. import bag
from .. import economy
from ..item_basic_data import BASIC_DATA
from ..._lang import text
from ..json2items import json2items

class Pouch(Item):
    def on_register(self):
        self.basic_data = {
            "display_name": "收纳袋",
            "display_message": "收纳物品\n \x00",
            "items": [],
            "price": 10,
            "maximum_stack": 16,
            "max_item_count": 16,
        }
        self.item_id = "pouch"

    def _after_register(self):
        self.update_info()

    def update_info(self):
        item_list = json2items(self.data["items"])
        display_info = (
            self.data["display_message"].split("\x00")[0]
            + f"\x00\n物品列表（\x01used/{self.data['max_item_count']}）："
        )
        length = 1
        used = 0
        for i in item_list:
            display_info += f"\n{length}. {i.data['display_name']} x{i.count}"
            used += i.count
            length += 1
        self.data["display_message"] = display_info.replace("\x01used", str(used))

    def use(self, args):
        args = args.split(" ")
        # self.data["items"] = self.data["items"].copy()
        if args[0] in ["put", "--put"]:
            return self.put_item(args)
        elif args[0] in ["get", "--get"]:
            return self.get_item(args)
        elif args[0] in ["upgrade", "--upgrade"]:
            if len(args) >= 2:
                count = int(args[1])
            else:
                count = 4
            if economy.use_vimcoin(self.user_id, count * 1.25):
                self.data["max_item_count"] += count
                return [text("currency.ok")]
            else:
                return [text("currency.no_money", [1.25 * count], self.user_id)]
        else:
            return [text("pouch.help", [], self.user_id)]

    def get_item(self, args):
        item = self.data["items"][int(args[1]) - 1]
        _item = json2items.json2items(self.data["items"])[int(args[1]) - 1]
        if len(args) < 3:
            count = item["count"]
        else:
            count = int(args[2])
            if count > item["count"] or count < 0:
                raise IllegalQuantityException(count)

        bag.add_item(self.user_id, item["id"], item["count"], item["data"])
        if count == item["count"]:
            self.data["items"].pop(int(args[1]) - 1)
        else:
            self.data["items"][int(args[1]) - 1]["count"] -= count

        self.update_info()
        return [text("pouch.got", [_item.data["display_name"], count], self.user_id)]

    def get_free_count(self):
        used = 0
        for i in self.data["items"]:
            used += i["count"]
        return self.data["max_item_count"] - used

    def put_item(self, args):
        item = bag.get_user_bag(self.user_id)[int(args[1]) - 1]
        count = item.count
        item_id = item.item_id
        if len(args) < 3:
            args.append(str(count))
        if count < int(args[2]) or int(args[2]) < 0:
            raise IllegalQuantityException(args[2])
        if int(args[2]) > self.get_free_count():
            return [text("pouch.not_enough_space", [], self.user_id)]

        # 处理nbt
        nbt = item.data.copy()
        for key in list(BASIC_DATA.keys()):
            try:
                if nbt[key] == BASIC_DATA[key]:
                    nbt.pop(key)
            except BaseException:
                pass
        for key in list(item.basic_data.keys()):
            try:
                if nbt[key] == item.basic_data[key]:
                    nbt.pop(key)
            except BaseException:
                pass

        item.count -= int(args[2])
        self.data["items"].append({"id": item_id, "count": int(args[2]), "data": nbt})
        self.update_info()
        _item = json2items.json2items([self.data["items"][-1]])[0]

        bag.add_item(self.user_id, self.item_id, 1, self.data)
        self.count -= 1
        return [
            text("pouch.put", [_item.data["display_name"], int(args[2])], self.user_id)
        ]

    def add(self, count, _data=...):
        if self.data["items"]:
            return 0
        return super().add(count, _data)
