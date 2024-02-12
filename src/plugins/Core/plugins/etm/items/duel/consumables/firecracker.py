import random
from types import NoneType
from ....duel.item import CannotUse, Returned
from ....duel.item.consumables import DuelConsumables
from ....duel.entity.user import User
from ....._utils import *
from ....duel.buff.CriticalStrikeHarmIncreased import CriticalStrikeHarmIncreased


class Firecracker(DuelConsumables):

    def __init__(self, count, data, user_id):
        super().__init__(count, data, user_id)
        self.DUEL_ITEM_TYPE = "consumables"

    def on_register(self) -> None:
        self.item_id = "firecracker"
        self.setup_basic_data(
            display_name=self.text("display_name"),
            display_message=self.text("display_message"),
            maximum_stack=16
        )
    
    async def duel_use(self) -> NoneType:
        await super().duel_use()
        if not isinstance(self.entity, User):
            self.entity.logger.log("unsupported_not_user")
            raise CannotUse
        entities = [entity for entity in self.entity.logger.scheduler.entities if entity.hp > 0 and entity.team_id != self.entity.team_id]
        if not entities:
            self.entity.logger.log("no_entity", [])
            raise CannotUse
        text = ""
        length = 0
        for entity in entities:
            length += 1
            text += lang.text(
                "duel_user.attack_menu_item",
                [length, entity.name, entity.team_id],
                self.user_id,
            )
        await self.entity.send("duel_user.attack_menu", [text, length + 1])
        choice = await self.entity.receive_reply(
            choices=[str(i) for i in range(1, length + 2)], default=str(length + 1)
        )
        if choice is None or choice == str(length + 1):
            raise Returned
        self.entity.logger.add_attack_log(
            entities[int(choice) - 1].attacked(
                20,
                self.entity,
                attack_type="physical"
            )
        )
        self.entity.logger.add_attack_log(
            self.entity.attacked(
                3,
                self.entity,
                attack_type="physical"
            )
        )
        if random.random() <= 0.03:
            buff = CriticalStrikeHarmIncreased(self.entity, 3)
            buff.adhesion = 7
            buff.apply()
        self.used()
        
