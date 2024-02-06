from typing import Self
from ._utils import *
from .etm.user import get_hp, remove_hp
from .etm.duel.entity.user import User

# import asyncio

# class DuelUser(User):

#     def attacked(self, harm: float, entity: Self, dodgeable: bool = True) -> float:
#         harm = super().attacked(harm, entity, dodgeable)
#         remove_hp(int(self.user_id), harm)
#         return harm

#     # async def sync_hp(self) -> None:
#     #     while self.hp != 0:
#     #         await asyncio.sleep(0.1)
#     #         self.hp = get_hp(int(self.user_id))
