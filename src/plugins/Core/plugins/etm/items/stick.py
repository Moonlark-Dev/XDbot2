from ..duel.entity import Entity
from ..duel.item.weapons import DuelWeapons


class Stick(DuelWeapons):
    def on_register(self):
        self.item_id = "stick"
        self.basic_data = {
            "display_name": self.text("display_name"),
            "display_message": self.text("display_message", [self.user_id]),
            "price": 3,
            "maximum_stack": 16
        }

    def on_attack(self, entity: Entity, entities: list[Entity]) -> None:
        entity.attacked(self.get_harm(2), self.entity)

