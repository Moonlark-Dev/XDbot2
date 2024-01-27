from typing import Optional
from .entity import Entity


class Scheduler:
    def __init__(self, entities: list[Entity]) -> None:
        self.entities: list[Entity] = entities

    def start(self) -> None:
        while (entity := self.get_entity()) and self.is_finished():
            entity.action(self.entities)
            for e in self.entities:
                e.reduce_action_value(entity.get_action_value())

    def sort_entities(self) -> None:
        self.entities = sorted(self.entities, key=lambda e: e.get_action_value())

    def get_entity(self) -> Optional[Entity]:
        self.sort_entities()
        for e in self.entities:
            if e.hp != 0:
                return e

    def is_finished(self) -> bool:
        teams = {}
        for e in self.entities:
            if e.hp == 0:
                continue
            if e.team_id not in teams:
                teams[e.team_id] = 0
            teams[e.team_id] += 1
        return len(teams.keys()) < 2
