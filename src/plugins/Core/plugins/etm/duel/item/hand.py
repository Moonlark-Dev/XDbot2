from typing import TYPE_CHECKING
from .weapons import DuelWeapons

if TYPE_CHECKING:
    from ..entity import Entity


class Hand(DuelWeapons):
    def on_register(self) -> None:
        self.item_id = "hand"
        self.basic_data = {
            "display_name": self.text("display_name"),
            "display_message": self.text("display_message"),
        }
        # self.ATTACK_TYPE = "single"

    def on_attack(self, entity: Entity, entities: list[Entity]) -> None:
        entity.attacked(self.get_harm(5), self.entity)
