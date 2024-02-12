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
        # self.action_choice: int = 0

    def set_output(self, bot: Bot, event: MessageEvent) -> None:
        self.bot = bot
        self.event = event
        self.auto = False

    async def send(self, key: str, _format: list[Any] = []):
        # self.logger.create_block()
        return await send_message(self.bot, self.event, key, _format)
        # self.logger.clear()
        # lang.text("sign.hr", [], self.user_id).join(self.logger.logs)
        # self._matcher = on_message(to_me())
        # self._matcher.handle()(self.get_action_choice)

    async def receive_reply(
        self,
        timeout: int = 30,
        choices: Optional[list[str]] = None,
        default: Optional[str] = None,
    ) -> Optional[str]:
        matcher = on_message()
        choice = None

        async def handler(event: MessageEvent) -> None:
            nonlocal choice
            if event.get_user_id() != self.user_id:
                await matcher.finish()
            message = event.get_plaintext()
            if choices and message not in choices:
                await finish(
                    "duel_user.unknown_choice", [message, choices], event.user_id
                )
            choice = message
            matcher.destroy()

        matcher.append_handler(handler)
        for _ in range(timeout):
            await asyncio.sleep(1)
            if choice is not None:
                return choice
        return default

    async def action(self, entities: list[Entity]) -> None:
        await super().action(entities)  # type: ignore
        if not self.auto:
            self.logger.add_action_queue()
            self.logger.create_block()
            await self.send(
                "duel_user.query",
                [lang.text("sign.hr", [], self.user_id).join(self.logger.logs)],
            )
            self.logger.clear()
            action_choice = int(
                await self.receive_reply(choices=["1", "3"], default="3") or "3"
            )
        else:
            action_choice = 3
        match action_choice:
            case 3:
                self.logger.log("skipped", [])
            case 2:
                pass
            case 1:
                await self.attack_action(entities)

    async def attack_action(self, _entities: list[Entity]) -> None:
        entities = [e for e in _entities if e.team_id != self.team_id]
        if not entities:
            self.logger.log("no_entity", [])
            return await self.action(_entities)
        if self.items["weapons"].ATTACK_RANGE == "all":
            return self.items["weapons"].on_attack(self, entities)
        text = ""
        length = 0
        for entity in entities:
            length += 1
            text += lang.text(
                "duel_user.attack_menu_item",
                [length, entity.name, entity.team_id],
                self.user_id,
            )
        await self.send("duel_user.attack_menu", [text, length + 1])
        choice = await self.receive_reply(
            choices=[str(i) for i in range(1, length + 2)], default=str(length + 1)
        )
        if (choice or str(length + 1)) == str(length + 1):
            return await self.action(_entities)
        entity = entities[int(choice) - 1]  # type: ignore
        self.items["weapons"].on_attack(entity, entities)

    def check_lock(self) -> None:
        if Json(f"duel2/lock.json")[self.user_id]:
            raise UserDataLocked
        Json(f"duel2/lock.json")[self.user_id] = True

    def __del__(self) -> None:
        Json(f"duel2/users/{self.user_id}.json")["items"] = {
            "weapons": {
                "id": self.items["weapons"].item_id,
                "count": self.items["weapons"].count,
                "data": self.items["weapons"].data,
            },
            "passive": [
                {"id": item.item_id, "count": item.count, "data": item.data}
                for item in self.items["passive"]
            ],
            "other": [
                {"id": item.item_id, "count": item.count, "data": item.data}
                for item in self.items["other"]
            ],
        }
        Json(f"duel2/lock.json")[self.user_id] = False

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
