from .item import Item
from ..duel.monomer import load_json


class Weapons(Item):
    def on_register(self):
        self.basic_data["maximum_stack"] = 1
        self.basic_data["price"] = 20
        self.item_id = "weapons"
        self.basic_data["useable"] = False

    def _after_register(self):
        self.data["display_name"] = (
            kit_data := load_json(f"kits/{self.data['kit']}.json")
        )["weapons"]["name"]
        self.data["display_message"] = f"所属套装：{kit_data['name']}\n" "武器（暂无说明）"


class Ball(Item):
    def on_register(self):
        self.basic_data["maximum_stack"] = 1
        self.basic_data["price"] = 40
        self.item_id = "ball"
        self.basic_data["useable"] = False

    def _after_register(self):
        self.data["display_name"] = (
            kit_data := load_json(f"kits/{self.data['kit']}.json")
        )["ball"]["name"]
        self.data["display_message"] = f"所属套装：{kit_data['name']}\n" "面位球（暂无说明）"
