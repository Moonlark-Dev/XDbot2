from typing import TYPE_CHECKING
from ...._utils import *

if TYPE_CHECKING:
    from ..entity import Entity


class Buff:
    def __init__(self, entity: "Entity") -> None:
        self.buff_id: str = ""
        self.name: str = ""  # TODO
        self.description: str = "无描述"  # TODO
        self.adhesion: int = 0
        self.entity = entity
        if hasattr(self.entity, "user_id"):
            self.user_id = getattr(self.entity, "user_id")
        else:
            self.user_id = "default"

    def apply(self) -> None:
        self.entity.buff.append(self)

    def text(self, key: str, format_: list[Any] = []) -> str:
        return lang.text(f"{self.buff_id}.{key}", format_, self.user_id)

    def after_action(self) -> None:
        self.adhesion -= 1
        if self.adhesion <= 0:
            self.on_effect_end()
            self.entity.buff.remove(self)
        del self

    def on_effect_end(self) -> None:
        pass

    def on_start(self) -> None:
        pass

    def on_action(self, entities: "list[Entity]") -> None:
        pass

    def on_attack(self, harm: float) -> float:
        return harm

    def on_attacked(self, harm: float, entity: "Entity") -> float:
        return harm
