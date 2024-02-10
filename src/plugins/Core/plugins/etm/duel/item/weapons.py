import random
from ...._utils import *

# from ...bag import add_item
from typing import TYPE_CHECKING, Literal
from ..item import DuelItem

if TYPE_CHECKING:
    from ..entity import Entity
else:
    Entity = None
from typing import Callable

add_item: Callable[[str, str, int, dict], None]


class DuelWeapons(DuelItem):
    ATTACK_TYPE: Literal["single", "all"]


    def __init__(self, count, data, user_id):
        super().__init__(count, data, user_id)
        self.DUEL_ITEM_TYPE = "weapons"
        self.ATTACK_TYPE = "single"

    def on_attack(self, entity: Entity, entities: list[Entity]) -> None:
        pass

    def get_harm(self, basic_harm: float) -> float:
        harm = basic_harm
        for item in self.entity.items["passive"]:
            harm = item.on_attack(harm) or harm
        for buff in self.entity.buff:
            harm = buff.on_attack(harm) or harm
        if random.random() <= self.entity.critical_strike[0]:
            harm *= self.entity.critical_strike[1]
        return harm

    def use_item(self):
        data = Json(f"duel2/users/{self.user_id}.json")
        if not data["items"]:
            data["items"] = {}
        original_weapons: dict | None = data["items"].get("weapons")
        data["items"]["weapons"] = {"id": self.item_id, "count": 1, "data": self.data}
        data.changed_key.add("items")
        if original_weapons:
            add_item(self.user_id, original_weapons["id"], 1, original_weapons["data"])
        self.count -= 1
        return lang.text("weapons.used", [self.data["display_name"]], self.user_id)
