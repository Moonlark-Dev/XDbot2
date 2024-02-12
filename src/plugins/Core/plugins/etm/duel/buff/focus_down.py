from typing import TYPE_CHECKING
from . import Buff

if TYPE_CHECKING:
    from plugins.Core.plugins.etm.duel.entity import Entity
from types import NoneType


class FocusDown(Buff):
    def __init__(self, entity: "Entity", value: float) -> None:
        super().__init__(entity)
        self.buff_id = "focus_down"
        self.value = value
        self.name = self.text("name")
        self.description = self.text("description", [self.value * 100])
        self.entity.focus -= value

    def on_effect_end(self) -> NoneType:
        self.entity.focus += self.value
        super().on_effect_end()
