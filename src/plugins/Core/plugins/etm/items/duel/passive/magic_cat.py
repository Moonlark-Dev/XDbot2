import random
from types import NoneType
from typing import TYPE_CHECKING
from ....duel.buff.focus_down import FocusDown
from ....duel.buff.harm_up import HarmUpInt
from ....duel.buff.CriticalStrikeChanceIncreased import CriticalStrikeChanceIncreased
from ....duel.item.relic import DuelRelic

if TYPE_CHECKING:
    from plugins.Core.plugins.etm.duel.entity import Entity


class MagicCatRelic(DuelRelic):

    def __init__(self, count, data, user_id):
        super().__init__(count, data, user_id)
        self.RELIC_SET_NAME = "magic_cat"

    def effect_two_piece_set(self) -> NoneType:
        self.entity.max_hp += 10
        return super().effect_two_piece_set()


class MagicCatHead(MagicCatRelic):

    def __init__(self, count, data, user_id):
        super().__init__(count, data, user_id)
        self.RELIC_TYPE = "head"

    def on_register(self) -> None:
        self.item_id = "magic_cat_head"
        self.setup_basic_data(
            display_name=self.text("display_name", []), maximum_stack=1
        )

    def on_attacked(self, harm: float, entity: "Entity") -> float:
        if entity.items["weapons"].ATTACK_TYPE != "physical":
            buff = CriticalStrikeChanceIncreased(self.entity, 0.5)
            buff.adhesion = 1
            self.entity.buff.append(buff)
        return super().on_attacked(harm, entity)

    def effect_four_piece_set(self) -> NoneType:
        self.entity.max_hp += 20
        return super().effect_four_piece_set()


class MagicCatBody(MagicCatRelic):

    def __init__(self, count, data, user_id):
        super().__init__(count, data, user_id)
        self.RELIC_TYPE = "body"

    def on_register(self) -> None:
        self.item_id = "magic_cat_body"
        self.setup_basic_data(display_name=self.text("display_name"), maximum_stack=1)

    def on_attacked(self, harm: float, entity: "Entity") -> float:
        if (
            entity.items["weapons"].ATTACK_TYPE != "physical"
            and random.random() <= 0.05
        ):
            harm = 0
            entity.logger.log("immune_to_attack")
        return harm


class MagicCatHand(MagicCatRelic):

    def __init__(self, count, data, user_id):
        super().__init__(count, data, user_id)
        self.RELIC_TYPE = "hand"

    def on_register(self) -> None:
        self.item_id = "magic_cat_hand"
        self.setup_basic_data(display_name=self.text("display_name"), maximum_stack=1)

    def on_attacked(self, harm: float, entity: "Entity") -> float:
        if random.random() <= 0.25:
            entity.logger.log("feel_cute", [])
            buff = FocusDown(entity, 0.05)
            buff.adhesion = 5
            entity.buff.append(buff)
        return super().on_attacked(harm, entity)


class MagicCatFoot(MagicCatRelic):

    def __init__(self, count, data, user_id):
        super().__init__(count, data, user_id)
        self.RELIC_TYPE = "foot"

    def on_register(self) -> None:
        self.item_id = "magic_cat_foot"
        self.setup_basic_data(display_name=self.text("display_name"), maximum_stack=1)

    def on_attacked(self, harm: float, entity: "Entity") -> float:
        if random.random() <= 0.01:
            harm = 0
            entity.logger.log("immune_to_attack")
        return super().on_attacked(harm, entity)


class MagicCatBall(MagicCatRelic):

    def __init__(self, count, data, user_id):
        super().__init__(count, data, user_id)
        self.RELIC_TYPE = "ball"

    def on_register(self) -> None:
        self.item_id = "magic_cat_ball"
        self.setup_basic_data(display_name=self.text("display_name"), maximum_stack=1)

    def on_attacked(self, harm: float, entity: "Entity") -> float:
        if entity.items["weapons"].ATTACK_TYPE == "physical":
            harm *= 1.5
            buff = HarmUpInt(entity, 10)
            buff.adhesion = 1
            buff.apply()
        return super().on_attacked(harm, entity)


class MagicCatRope(MagicCatRelic):

    def __init__(self, count, data, user_id):
        super().__init__(count, data, user_id)
        self.RELIC_TYPE = "rope"

    def on_register(self) -> None:
        self.item_id = "magic_cat_rope"
        self.setup_basic_data(display_name=self.text("display_name"), maximum_stack=1)


from ....duel.item.weapons import DuelWeapons


class MagicStick(DuelWeapons):

    def __init__(self, count, data, user_id):
        super().__init__(count, data, user_id)
        self.ATTACK_TYPE = "magic"
        self.SET_NAME = "magic_cat"

    def on_register(self) -> None:
        self.item_id = "magic_stick"
        self.setup_basic_data(
            display_name=self.text("display_name"),
            display_message=self.text("display_message"),
            maximum_stack=1,
        )

    def on_attack(self, entity: "Entity", entities: "list[Entity]") -> NoneType:
        self.entity.logger.add_attack_log(
            entity.attacked(self.get_harm(12), entity)
        )
        if random.random() <= 0.02:
            self.entity.critical_strike = (
                self.entity.critical_strike[0],
                self.entity.critical_strike[1] + 30,
            )
            self.entity.logger.log("magic_cat_critical_strike_harm_increased")
