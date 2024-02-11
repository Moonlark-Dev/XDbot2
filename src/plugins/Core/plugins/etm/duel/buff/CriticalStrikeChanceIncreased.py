from typing import TYPE_CHECKING
from . import Buff

if TYPE_CHECKING:
    from plugins.Core.plugins.etm.duel.entity import Entity
from types import NoneType


class CriticalStrikeChanceIncreased(Buff):
    def __init__(self, entity: "Entity", value: float) -> None:
        super().__init__(entity)
        self.buff_id = "critical_strike_chance_increased"
        self.value = value
        self.name = self.text("name")
        self.description = self.text("description", [self.value * 100])

    def on_action(self, entities: "list[Entity]") -> NoneType:
        super().on_action(entities)
        self.entity.logger.log("critical_strike_chance_increased", [self.value * 100])
        self.entity.critical_strike = (
            self.entity.critical_strike[0] + self.value,
            self.entity.critical_strike[1],
        )

    def after_action(self) -> NoneType:
        self.entity.critical_strike = (
            self.entity.critical_strike[0] - self.value,
            self.entity.critical_strike[1],
        )
        return super().after_action()
