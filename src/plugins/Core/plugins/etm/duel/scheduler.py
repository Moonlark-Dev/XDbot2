from typing import Optional
from .entity import Entity
from .logger import Logger


class Scheduler:
    def __init__(self, entities: list[Entity], user_id: str = "default") -> None:
        self.original_entities: list[Entity] = entities
        self.entities = self.original_entities.copy()
        self.logger = Logger(user_id, self)
        for i in range(len(self.entities)):
            self.entities[i].set_logger(self.logger)

    async def start(self) -> None:
        while (entity := self.get_entity()) and not self.is_finished():
            self.logger.add_action_title(entity)
            self.logger.add_entity_hp(entity)
            reduce_value = entity.get_action_value()
            for e in self.entities:
                e.reduce_action_value(reduce_value)
            await entity.action(self.entities)
            self.logger.create_block()
        self.logger.create_block()
        self.logger.log("finished")

    def sort_entities(self) -> None:
        self.entities = sorted(self.original_entities, key=lambda e: e.get_action_value())

    def get_entity(self) -> Optional[Entity]:
        self.sort_entities()
        for e in self.entities:
            if e.hp != 0:
                return e

    def is_finished(self) -> bool:
        teams = {}
        for e in self.entities:
            if e.hp <= 0:
                continue
            if e.team_id not in teams:
                teams[e.team_id] = 0
            teams[e.team_id] += 1
        return len(teams.keys()) < 2
