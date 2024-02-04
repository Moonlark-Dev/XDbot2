from typing import TYPE_CHECKING, Optional, cast
from ..item.passive import DuelPassiveItem
from ..item.weapons import DuelWeapons
from ..entity import Entity

# from ...json2items import json2items
from ..item import DuelItem
from ...._utils import *

if TYPE_CHECKING:
    from plugins.Core.plugins.etm.item import Item
else:
    Item = None


class UserDataLocked(Exception):
    pass


json2items: Callable[[list[dict], Optional[str]], list[Item]]


class User(Entity):
    def __init__(self, user_id: str, hp: int = -1) -> None:
        super().__init__()
        self.user_id: str = user_id
        self.check_lock()
        self.auto: bool = False
        self.get_items()
        self.setup_items_effect()
        self.hp = hp

    def check_lock(self) -> None:
        if Json(f"duel2/lock.json")[self.user_id]:
            raise UserDataLocked
        Json(f"duel2/lock.json")[self.user_id] = True

    def __del__(self) -> None:
        Json(f"duel2/lock.json")[self.user_id] = True

    def get_items(self) -> None:
        items: dict = Json(f"duel2/users/{self.user_id}.json").get("items", {})
        if weapons := items.get("weapons"):
            self.items["weapons"] = cast(
                DuelWeapons, json2items([weapons], self.user_id)[0]
            )
        self.items["passive"] = cast(
            list[DuelPassiveItem], json2items(items.get("passive", []), self.user_id)
        )
        self.items["other"] = cast(
            list[DuelItem], json2items(items.get("other", []), self.user_id)
        )
