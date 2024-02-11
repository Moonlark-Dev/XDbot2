from typing import TYPE_CHECKING, Literal
from ...item import Item
from ...exception import UserDataLocked
from ...._utils import *

if TYPE_CHECKING:
    from ..entity import Entity
else:
    Entity = None


class DuelItem(Item):
    DUEL_ITEM_TYPE: Literal["weapons", "consumables", "passive", "active", "other"]

    def init_duel(self, entity: Entity) -> None:
        self.entity: Entity = entity

    def duel_use(self) -> None:
        pass

    def use_item(self) -> None:
        if Json(f"duel2/lock.json")[self.user_id]:
            raise UserDataLocked
