from typing import TYPE_CHECKING
from . import Buff

if TYPE_CHECKING:
    from plugins.Core.plugins.etm.duel.entity import Entity
from types import NoneType


class CriticalStrikeHarmIncreased(Buff):
    def __init__(self, entity: "Entity", value: float) -> None:
        super().__init__(entity)
        self.buff_id = "critical_strike_harm_increased"
        self.value = value
        self.name = self.text("name")
        self.description = self.text("description", [self.value * 100])
        self.entity.logger.log("critical_strike_harm_increased", [self.value * 100])
        self.entity.critical_strike = (
            self.entity.critical_strike[0],
            self.entity.critical_strike[1] + self.value,
        )

    def after_action(self) -> NoneType:
        self.entity.critical_strike = (
            self.entity.critical_strike[0],
            self.entity.critical_strike[1] - self.value,
        )
        return super().after_action()
