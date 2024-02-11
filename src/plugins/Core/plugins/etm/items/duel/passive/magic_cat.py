from typing import TYPE_CHECKING

from ....duel.buff.CriticalStrikeChanceIncreased import CriticalStrikeChanceIncreased
from ....duel.item.relic import DuelRelic

if TYPE_CHECKING:
    from plugins.Core.plugins.etm.duel.entity import Entity


class MagicCatHead(DuelRelic):

    def __init__(self, count, data, user_id):
        super().__init__(count, data, user_id)
        self.RELIC_SET_NAME = "magic_cat"
        self.RELIC_TYPE = "head"

    def on_register(self) -> None:
        self.item_id = "magic_cat_head"
        self.setup_basic_data(
            display_name=self.text("display_name", []),
            display_message=self.text("display_message", []),
            maximum_stack=1,
        )

    def on_attacked(self, harm: float, entity: "Entity") -> float:
        if entity.items["weapons"].ATTACK_TYPE != "physical":
            buff = CriticalStrikeChanceIncreased(self.entity, 0.5)
            buff.adhesion = 1
            self.entity.buff.append(buff)
        return super().on_attacked(harm, entity)
