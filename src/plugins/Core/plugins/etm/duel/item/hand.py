from typing import TYPE_CHECKING

# from plugins.Core.plugins.etm.duel.entity import Entity
from .weapons import DuelWeapons

if TYPE_CHECKING:
    from ..entity import Entity
else:
    Entity = None


class Hand(DuelWeapons):
    def on_register(self) -> None:
        self.item_id = "hand"
        self.basic_data = {
            "display_name": self.text("display_name"),
            "display_message": self.text("display_message"),
        }
    
    def init_duel(self, entity: Entity) -> None:
        super().init_duel(entity)
        entity.critical_strike = 0.25, 1.3

    def on_attack(self, entity: Entity, entities: list[Entity]) -> None:
        self.entity.logger.add_attack_log(
            entity,
            entity.attacked(self.get_harm(3), self.entity)
        )
