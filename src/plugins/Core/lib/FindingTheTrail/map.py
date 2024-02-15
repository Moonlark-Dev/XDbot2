from typing import Literal
from .const import *
import random

def generate(row: int = 6, column: int = 8, wall_ratio: float = 0.2) -> list[list[int]]:
    game_map = [[NULL for _ in range(column)] for _ in range(row)]
    for r in range(row):
        for c in range(column):
            if r in [0, 5] or c in [0, 7]:
                game_map[r][c] = WALL
            elif random.random() <= wall_ratio:
                game_map[r][c] = random.choice([WALL, WALL, SPECIAL])
    while True:
        col = random.randint(1,6)
        if game_map[1][col] not in [WALL, START]:
            game_map[0][col] = TERMINAL
        break
    while True:
        r = random.randint(1,4)
        c = random.randint(1,5)
        if game_map[r][c] == NULL:
            game_map[r][c] = START
            break
    return game_map


if __name__ == "__main__":
    game_map = generate()
    print("\n".join(str(row) for row in game_map))