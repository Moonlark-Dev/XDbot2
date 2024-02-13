from typing import TYPE_CHECKING, Literal, Optional, Self, cast

if TYPE_CHECKING:
    from plugins.Core.plugins.etm.duel.entity import Entity
from ...._utils import *
from .passive import DuelPassiveItem

GAIN_LIST = Literal[
    "critical_strike_chance",
    "critical_strike_harm",
    "harm",
    "harm_%",
    "hp",
    "hp_%",
    "speed",
    "defense",
    "defense_%",
    "focus",
    "dodge",
]
RELICS_EXECUTION_PRIORITY = ["head", "body", "foot", "hand"]


class DuelRelic(DuelPassiveItem):
    RELIC_TYPE: Literal["head", "body", "foot", "hand", "rope", "ball"]
    RELIC_SET_NAME: Optional[str]

    def __init__(self, count, data, user_id):
        super().__init__(count, data, user_id)
        self.RELIC_SET_NAME = None
        self.attack_power_up = [0, 0]

    def get_gain_string(self) -> str:
        return "\n".join(
            [
                lang.text(
                    f"relic.gain_{gain['type']}",
                    [
                        (
                            gain["value"] * 100
                            if isinstance(gain["value"], float)
                            else gain["value"]
                        )
                    ],
                    self.user_id,
                )
                for gain in self.data["gain"]
            ]
        )

    def _after_register(self):
        super()._after_register()
        if "gain" not in self.data:
            self.data["gain"] = []
        if "level" not in self.data:
            self.data["level"] = 0
        self.data["display_message"] = (
            self.text("display_message", [self.get_gain_string()]),
        )

    def effect_gain(self) -> None:
        for gain in self.data["gain"]:
            match cast(GAIN_LIST, gain["type"]):
                case "critical_strike_chance":
                    self.entity.critical_strike = (
                        self.entity.critical_strike[0] + gain["value"],
                        self.entity.critical_strike[1],
                    )
                case "critical_strike_harm":
                    self.entity.critical_strike = (
                        self.entity.critical_strike[0],
                        self.entity.critical_strike[1] + gain["value"],
                    )
                case "defense":
                    self.entity.defense += gain["value"]
                case "defense_%":
                    self.entity.defense *= 1 + gain["value"]
                case "dodge":
                    self.entity.dodge += gain["value"]
                case "focus":
                    self.entity.focus += gain["value"]
                case "harm":
                    self.attack_power_up[0] += gain["value"]
                case "harm_%":
                    self.attack_power_up[1] += gain["value"]
                case "hp":
                    self.entity.max_hp += gain["value"]
                case "hp_%":
                    self.entity.max_hp *= 1 + gain["value"]
                case "speed":
                    self.entity.speed += gain["value"]

    def on_attack(self, harm: float) -> float:
        harm = super().on_attack(harm) or harm
        harm += self.attack_power_up[0]
        harm *= 1 + self.attack_power_up[1]
        return harm

    def init_duel(self, entity: "Entity") -> None:
        super().init_duel(entity)
        # 共鸣
        if (
            self.RELIC_TYPE == "ball"
            and self.entity.items["weapons"].SET_NAME == self.RELIC_SET_NAME
        ):
            pass
        # 二件套
        same_set_items = [
            i
            for i in self.entity.items["passive"]
            if isinstance(i, DuelRelic) and i.RELIC_SET_NAME == self.RELIC_SET_NAME
        ]
        if (
            len(same_set_items) >= 2
            and sorted(
                same_set_items,
                key=lambda i: RELICS_EXECUTION_PRIORITY.index(i.RELIC_TYPE),
            )[0]
            == self
        ):
            self.effect_two_piece_set()
        # 四件套
        if len(same_set_items) >= 4 and self.RELIC_TYPE == "head":
            self.effect_four_piece_set()
        # 绳结
        if (
            self.RELIC_TYPE == "ball"
            and self.get_rope_set_name() == self.RELIC_SET_NAME
        ):
            self.effect_knot()
        # 六件套
        if self.RELIC_TYPE == "ball" and len(same_set_items) >= 6:
            self.effect_six_piece_set()

    def effect_knot(self) -> None:
        pass

    def get_rope_set_name(self) -> Optional[str]:
        rope = [
            i
            for i in self.entity.items["passive"]
            if isinstance(i, DuelRelic) and i.RELIC_TYPE == "rope"
        ]
        if len(rope) >= 1:
            return rope[0].RELIC_SET_NAME

    def effect_resonance(self) -> None:
        pass

    def effect_four_piece_set(self) -> None:
        pass

    def effect_six_piece_set(self) -> None:
        pass

    def effect_two_piece_set(self) -> None:
        pass
