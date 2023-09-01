from .item import Item
from ..duel.monomer import load_json
from .._utils import Json, lang


class Weapons(Item):
    def on_register(self):
        self.basic_data["maximum_stack"] = 1
        self.basic_data["price"] = 20
        self.item_id = "weapons"
        self.basic_data["useable"] = True

    def use(self, argv: str):
        if not self.data["useable"]:
            return ["失败：物品无法被使用"]
        if not argv:
            old_weapon = Json(f"duel/u{self.user_id}.json").get(
                "weapons", "leather_case"
            )
            Json(f"duel/u{self.user_id}.json")["weapons"] = self.data["kit"]
            self.data["kit"] = old_weapon
            self._after_register()
            return [lang.text("currency.ok", [], self.user_id)]
        return [lang.text("random_number.argerr", [], self.user_id)]

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
        self.basic_data["useable"] = True

    def _after_register(self):
        self.data["display_name"] = (
            kit_data := load_json(f"kits/{self.data['kit']}.json")
        )["ball"]["name"]
        self.data["display_message"] = f"所属套装：{kit_data['name']}\n" "面位球（暂无说明）"

    def use(self, argv: str):
        if not self.data["useable"]:
            return ["失败：物品无法被使用"]
        if not argv:
            old_ball = Json(f"duel/u{self.user_id}.json").get("ball", "leather_case")
            Json(f"duel/u{self.user_id}.json")["ball"] = self.data["kit"]
            self.data["kit"] = old_ball
            self._after_register()
            return [lang.text("currency.ok", [], self.user_id)]
        return [lang.text("random_number.argerr", [], self.user_id)]
