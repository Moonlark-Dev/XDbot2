import asyncio
from typing import TYPE_CHECKING, Optional, Self, cast

from ...exception import UserDataLocked
from ..item.passive import DuelPassiveItem
from ..item.weapons import DuelWeapons
from ..entity import Entity
from nonebot.rule import to_me
from ..item import DuelItem
from ...._utils import *

if TYPE_CHECKING:
    from plugins.Core.plugins.etm.item import Item
else:
    Item = None


json2items: Callable[[list[dict], Optional[str]], list[Item]]


class User(Entity):
    def __init__(self, user_id: str, hp: int = -1) -> None:
        super().__init__()
        self.user_id: str = user_id
        if hp != -1:
            self.check_lock()
        self.auto: bool = True
        self.get_items()
        self.setup_items_effect()
        self.hp = hp
        self.action_choice: int = 0

    def set_output(self, bot: Bot, event: MessageEvent) -> None:
        self.bot = bot
        self.event = event
        self.auto = False

    async def send_action_menu(self):
        # TODO 独立此类函数
        self.logger.create_block()
        self._message_id = await send_message(
            self.bot,
            self.event,
            "query",
            [
                lang.text("sign.hr", [], self.user_id).join(self.logger.logs)
            ]
        )
        self.logger.clear()
        self._matcher = on_message(to_me())
        self._matcher.handle()(self.get_action_choice)

    async def get_action_choice(self, event: MessageEvent, matcher: Matcher) -> None:
        if (event.reply is None 
                or event.reply.message_id != self._message_id):
            await matcher.finish()
        try:
            self.action_choice = int(event.message.extract_plain_text().strip())
            matcher.destroy()
        except ValueError:
            await matcher.finish()
        

    async def action(self, entities: list[Entity]) -> None:
        await super().action(entities)  # type: ignore
        if not self.auto:
            self.logger.add_action_queue(entities)
            await self.send_action_menu()
            for _ in range(30):
                await asyncio.sleep(1)
                if self.action_choice != 0:
                    break
            else:
                self._matcher.destroy()
                self.action_choice = 3
        else:
            self.action_choice = 3
        

    def check_lock(self) -> None:
        if Json(f"duel2/lock.json")[self.user_id]:
            raise UserDataLocked
        Json(f"duel2/lock.json")[self.user_id] = True

    def __del__(self) -> None:
        Json(f"duel2/lock.json")[self.user_id] = True

    def get_items(self) -> None:
        items: dict = Json(f"duel2/users/{self.user_id}.json").get("items", {})
        if weapons := items.get("weapons"):
            self.items["weapons"] = cast(
                DuelWeapons, json2items([weapons], self.user_id)[0]
            )
        self.items["passive"] = cast(
            list[DuelPassiveItem], json2items(items.get("passive", []), self.user_id)
        )
        self.items["other"] = cast(
            list[DuelItem], json2items(items.get("other", []), self.user_id)
        )
