from typing import TypedDict
from .const import *
import copy


def get_item_by_pos(pos: tuple[int, int], game_map: list[list[int]]) -> int:
    return game_map[pos[0]][pos[1]]


def get_start_pos(game_map: list[list[int]]) -> tuple[list[list[int]], tuple[int, int]]:
    for r in range(len(game_map)):
        for c in range(len(game_map[r])):
            if get_item_by_pos((r, c), game_map) == START:
                game_map[r][c] = NULL
                return game_map, (r, c)
    raise ValueError


DR = (-1, 1, 0, 0)
DC = (0, 0, -1, 1)


def get_moved_pos(original_pos: tuple[int, int], direction: int) -> tuple[int, int]:
    return (original_pos[0] + DR[direction - 1], original_pos[1] + DC[direction - 1])


def is_item_moveable(item: int) -> bool:
    return item in [NULL, TERMINAL, PISTON]


def get_moveable_direction(
    game_map: list[list[int]], pos: tuple[int, int]
) -> list[int]:
    return [
        i
        for i in range(1, 5)
        if is_item_moveable(get_item_by_pos(get_moved_pos(pos, i), game_map))
    ]


def get_back_direction(direction: int) -> int:
    return {LEFT: RIGHT, RIGHT: LEFT, UP: DOWN, DOWN: UP}[direction]


def move(
    game_map: list[list[int]], pos: tuple[int, int], direction: int
) -> tuple[list[list[int]], tuple[int, int]]:
    while True:
        pos = get_moved_pos(pos, direction)
        item = get_item_by_pos(pos, game_map)
        if not is_item_moveable(item):
            if item == SAND:
                game_map[pos[0]][pos[1]] = BROKEN_SAND
            return game_map, get_moved_pos(pos, get_back_direction(direction))
        elif item == TERMINAL:
            return game_map, pos
        elif item == PISTON:
            game_map[pos[0]][pos[1]] = WALL


# map = [
# [1, 1, 1, 3, 1, 1, 1, 1],
# [1, 0, 2, 0, 0, 0, 0, 1],
# [1, 0, 0, 0, 0, 0, 0, 1],
# [1, 1, 0, 0, 0, 0, 0, 1],
# [1, 0, 0, 0, 0, 0, 1, 1],
# [1, 1, 1, 1, 1, 1, 1, 1]
# ]
# pos = (1,6)
# for s in [4, 3, 1]:
#     map, pos = move(map, pos, s)
#     print(pos, s)
#     print("\n".join(str(row) for row in map))


class QueueItem(TypedDict):
    game_map: list[list[int]]
    direction: int
    original_pos: tuple[int, int]
    path: list[int]


def parse_broken_sand(game_map: list[list[int]]) -> list[list[int]]:
    for row in range(len(game_map)):
        for column in range(len(game_map[row])):
            if game_map[row][column] == BROKEN_SAND:
                game_map[row][column] = NULL
    return game_map


def search(game_map: list[list[int]], max_step: int = 12) -> list[int]:
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
        item["game_map"] = parse_broken_sand(item["game_map"])
        game_map, pos = move(item["game_map"], item["original_pos"], item["direction"])
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
        # print(item["path"])
        if len(item["path"]) >= max_step:
            return []
