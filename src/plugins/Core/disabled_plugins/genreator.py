from ..lib.FindingTheTrail.argv import ARGUMENTS
from ..lib.FindingTheTrail.map import generate
from ..lib.FindingTheTrail.search import (
    QueueItem,
    get_start_pos,
    get_moveable_direction,
    get_item_by_pos,
    move,
    parse_sand,
)
import copy
import multiprocessing


class Generator:

    def __init__(self, difficulty: str) -> None:
        self.pool = multiprocessing.Pool(4)
        self.difficulty = difficulty

    def search(self, game_map: list[list[int]], max_step: int = 12) -> list[int]:
        game_map, start_pos = get_start_pos(game_map)
        queue: list[QueueItem] = [
            {
                "direction": d,
                "game_map": copy.deepcopy(game_map),
                "original_pos": start_pos,
                "path": [d],
            }
            for d in get_moveable_direction(game_map, start_pos)
        ]
        while True:
            try:
                item = queue.pop(0)
            except IndexError:
                return []
            if get_item_by_pos(item["original_pos"], item["game_map"]) == TERMINAL:
                return item["path"][:-1]
            item["game_map"] = parse_sand(item["game_map"], item["original_pos"])
            game_map, pos = move(
                item["game_map"], item["original_pos"], item["direction"]
            )
            queue.extend(
                [
                    {
                        "direction": d,
                        "original_pos": pos,
                        "game_map": copy.deepcopy(game_map),
                        "path": item["path"] + [d],
                    }
                    for d in get_moveable_direction(game_map, pos)
                ]
            )
            if len(item["path"]) >= max_step:
                return []
            elif (
                len(item["path"]) >= 12 and len(multiprocessing.active_children()) <= 8
            ):
                self.pool.apply_async(self.generate)

    def generate(self) -> tuple[list[list[int]], list[int]]: ...
