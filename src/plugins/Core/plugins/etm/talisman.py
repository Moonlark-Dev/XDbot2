from .item import Item
from . import buff


class Talisman(Item):

    def on_register(self):
        self.item_id = "talisman"
        self.basic_data = {
            "display_name": "护符",
            "display_message": "在二十面骰子出 1 时有 75% 的概率取消扣除 50vi，生效 5 次",
            "maximum_stack": 8,
            "price": 100
        }

    def use_item(self):
        buff.give_buff(self.user_id, "护符", 1)
        return "护符已生效"
