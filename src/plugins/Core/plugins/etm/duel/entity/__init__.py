import math
from typing import TYPE_CHECKING, Self, TypedDict
from ..buff import Buff
import random
from ..item.hand import Hand

if TYPE_CHECKING:
    from ..item import DuelItem
    from ..item.weapons import DuelWeapons
    from ..item.passive import DuelPassiveItem
    from ..logger import Logger
else:
    DuelItem = None
    DuelWeapons = None
    DuelPassiveItem = None


class Items(TypedDict):
    weapons: DuelWeapons
    passive: list[DuelPassiveItem]
    other: list[DuelItem]


class Entity:
    def __init__(self) -> None:
        self.items: Items = {"weapons": Hand(1, {}, None), "other": [], "passive": []}
        self.buff: list[Buff] = []
        self.max_hp: int = 100
        self.hp = 0
        self.critical_strike: tuple[float, float] = 0.05, 1.5
        self.speed: int = 100
        self.reduced_action_value: float = 0
        self.name: str = ""
        self.shield: float = 0
        self.team_id: str = ""
        self.defense: int = 0
        self.focus: float = 0.5
        self.dodge: float = 0

    def set_logger(self, logger: 'Logger') -> None:
        self.logger = logger

    def attacked(self, harm: float, entity: Self, dodgeable: bool = True) -> float:
        if (
            random.random()
            >= math.sqrt(max((entity.focus - self.dodge) ** 2, (1 - self.dodge) ** 2))
            and dodgeable
        ):
            return 0
        if self.shield > harm:
            self.shield -= harm
            return harm
        elif self.shield > 0:
            harm -= self.shield
            self.shield = 0
        self.hp -= (h := harm / (1 + self.defense / 100))
        return h

    def get_action_value(self):
        return 10000 / self.speed - self.reduced_action_value

    def reduce_action_value(self, c: float) -> None:
        self.reduced_action_value += c
        if self.get_action_value() <= 0:
            self.reduced_action_value = 0

    async def action(self, entities: list[Self]) -> None:
        pass

    def setup_items_effect(self) -> None:
        items = self.items["passive"] + self.items["other"]
        if self.items["weapons"]:
            items.append(self.items["weapons"])
        for item in items:
            item.init_duel(self)
