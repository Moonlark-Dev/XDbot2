from .item import Item
from . import items
from . import bag
from . import economy
from .item_basic_data import BASIC_DATA

class Pouch(Item): 
    def on_register(self):
        self.basic_data = {
            "display_name": "收纳袋",
            "display_message": "收纳袋\x00",
            "items": [],
            "max_item_count": 16
        }
        self.item_id = "pouch"

    def update_info(self):
        item_list = items.json2items(self.data["items"])
        display_info = self.data["display_message"].split("\x00")[0] + "\x00\n物品列表（\x01used/\x01max）："
        length = 1
        for i in item_list:
            display_info += f"\n{length}. {i.data['display_name']} x{i.count}"
            length += 1
        self.data["display_message"] = display_info
    
    def use(self, args):
        args = args.split(" ")
        if args[0] in ["put", "--put"]:
            item = bag.get_user_bag(self.user_id)[int(args[1])]
            count = item.count
            item_id = item.item_id
            if count < int(args[1]):
                raise economy.IllegalQuantityException(args[1])
            elif len(args) < 3:
                args.append(count)
            
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
            self.data["items"].append({
                "id": item_id,
                "count": int(args[-1]),
                "data": nbt
            })
            bag.save_bags()
            self.update_info()
            return ["已添加"]

