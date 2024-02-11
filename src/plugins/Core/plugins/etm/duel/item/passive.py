from ..item import DuelItem
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..entity import Entity


class DuelPassiveItem(DuelItem):
    def __init__(self, count, data, user_id):
        super().__init__(count, data, user_id)
        self.DUEL_ITEM_TYPE = "passive"

    def on_attack(self, harm: float) -> float:
        return harm

    def on_attacked(self, harm: float, entity: 'Entity') -> float:
        return harm
