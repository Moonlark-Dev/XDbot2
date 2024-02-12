import math
from typing import TYPE_CHECKING, Literal, Self, TypedDict
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


class AttackResult(TypedDict):
    miss: bool
    type: Literal["physical", "magic"]
    original_hp: float
    original_shield: float
    harm: float


class Entity:
    def __init__(self) -> None:
        self.items: Items = {"weapons": Hand(1, {}, None), "other": [], "passive": []}
        self.buff: list[Buff] = []
        self.max_hp: int = 100
        self.hp = 0
        self.critical_strike: tuple[float, float] = 0.05, 1.5
        self.speed: int = 95
        self.reduced_action_value: float = 0
        self.name: str = ""
        self.shield: float = 0
        self.team_id: str = ""
        self.defense: int = 0
        self.focus: float = 0.5
        self.dodge: float = 0

    def set_logger(self, logger: "Logger") -> None:
        self.logger = logger

    def attacked(
        self, harm: float, entity: Self, dodgeable: bool = True
    ) -> AttackResult:
        result: AttackResult = {
            "miss": False,
            "original_hp": self.hp,
            "original_shield": self.shield,
            "harm": 0,
            "type": entity.items["weapons"].ATTACK_TYPE,
        }
        for item in self.items["passive"]:
            harm = item.on_attacked(harm, entity) or harm
        for buff in self.buff:
            harm = buff.on_attacked(harm, entity) or harm
        dodge = self.dodge * (self.focus / 2)
        if (
            random.random()
            >= math.sqrt(max((entity.focus - dodge) ** 2, (1 - dodge) ** 2))
            and dodgeable
        ):
            result["miss"] = True
            return result
        harm = round(harm, 1)
        if self.shield > harm:
            self.shield -= harm
            result["harm"] = harm
            return result
        elif self.shield > 0:
            harm -= self.shield
            self.shield = 0
        self.hp -= (h := round(harm / (1 + self.defense / 100), 1))
        self.hp = round(self.hp, 1)
        result["harm"] = result["original_shield"] + h
        return result

    def get_action_value(self):
        return 10000 / self.speed - self.reduced_action_value

    def reduce_action_value(self, c: float) -> None:
        self.reduced_action_value += c

    async def action(self, entities: list[Self]) -> None:
        self.reduced_action_value = 0

    def setup_items_effect(self) -> None:
        items = self.items["passive"] + self.items["other"]
        if self.items["weapons"]:
            items.append(self.items["weapons"])
        for item in items:
            item.init_duel(self)
