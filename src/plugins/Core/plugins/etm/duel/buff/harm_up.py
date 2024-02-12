from typing import TYPE_CHECKING
from . import Buff
if TYPE_CHECKING:
    from plugins.Core.plugins.etm.duel.entity import Entity
from types import NoneType


class HarmUpInt(Buff):
    def __init__(self, entity: "Entity", value: float) -> None:
        super().__init__(entity)
        self.buff_id = "harm_up_int"
        self.value = value
        self.name = self.text("name")
        self.description = self.text("description", [self.value * 100])
    
    def on_attack(self, harm: float) -> float:
        harm += self.value
        return super().on_attack(harm)
