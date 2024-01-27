import random
from typing import TYPE_CHECKING, Literal
from ..item import DuelItem

if TYPE_CHECKING:
    from ..entity import Entity


class DuelWeapons(DuelItem):
    # ATTACK_TYPE: Literal["single", "diffusion", "random"]

    def __init__(self, count, data, user_id):
        super().__init__(count, data, user_id)
        self.DUEL_ITEM_TYPE = "weapons"

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
