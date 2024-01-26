from typing import Self
from ..item import DuelItem
from ..buff import Buff

class Entity:
    def __init__(self) -> None:
        self.items: list[DuelItem] = []
        self.buff: list[Buff] = []
        self.max_hp: int = 100
        self.hp = 0
        self.speed: int = 0
        self.reduced_action_value: float = 0
        self.name: str = ""
        self.shield: int = 0
        self.team_id: str = ""

    def get_action_value(self):
        return 10000 / self.speed - self.reduced_action_value
    
    def reduce_action_value(self, c: float) -> None:
        self.reduced_action_value += c
        if self.get_action_value() <= 0:
            self.reduced_action_value = 0

    def action(self, entities: list[Self]) -> None:
        pass

    def setup_items_effect(self) -> None:
        for item in self.items:
            item.init_duel(self)
