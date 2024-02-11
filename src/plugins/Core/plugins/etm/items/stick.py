from ..duel.entity import Entity
from ..duel.item.weapons import DuelWeapons


class Stick(DuelWeapons):
    def on_register(self):
        self.item_id = "stick"
        self.basic_data = {
            "display_name": self.text("display_name"),
            "display_message": self.text("display_message", [self.user_id]),
            "price": 3,
            "maximum_stack": 16,
        }

    def init_duel(self, entity: Entity) -> None:
        super().init_duel(entity)
        self.entity.critical_strike = (0.25, 1.35)

    def on_attack(self, entity: Entity, entities: list[Entity]) -> None:
        self.entity.logger.add_attack_log(
            entity, entity.attacked(self.get_harm(7), self.entity)
        )
