from typing import cast
from ...user import get_hp
from ..item.passive import DuelPassiveItem
from ..item.weapons import DuelWeapons
from ..entity import Entity
from ...json2items import json2items
from ..item import DuelItem
from ...._utils import *

class User(Entity):

    def __init__(self, user_id: str) -> None:
        super().__init__()
        self.user_id: str = user_id
        self.auto: bool = False
        self.get_items()
        self.setup_items_effect()
        self.hp = get_hp(int(user_id))

    
    def get_items(self) -> None:
        items: dict = Json(f"duel2/users/{self.user_id}.json").get("items", [])
        if (weapons := items.get("weapons")):
            self.items["weapons"] = cast(DuelWeapons, json2items([weapons], self.user_id)[0])
        self.items["passive"] = cast(list[DuelPassiveItem], json2items(items.get("passive", []), self.user_id))
        self.items["other"] = cast(list[DuelItem], json2items(items.get("other", []), self.user_id))
    
