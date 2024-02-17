from .const import *
import random
from .argv import ARGUMENTS


def generate(
    row: int = 6,
    column: int = 8,
    blocks: list[tuple[int, float]] = ARGUMENTS["easy"]["map"]["blocks"],
) -> list[list[int]]:
    game_map = [[NULL for _ in range(column)] for _ in range(row)]
    for r in range(row):
        for c in range(column):
            if r in [0, row - 1] or c in [0, column - 1]:
                game_map[r][c] = WALL
                continue
            for block in blocks:
                if random.random() <= block[1]:
                    game_map[r][c] = block[0]
    while True:
        r = random.randint(1, row - 1)
        c = random.randint(1, column - 1)
        if game_map[r][c] == NULL:
            game_map[r][c] = START
            break
    while True:
        col = random.randint(1, row)
        if game_map[1][col] not in [WALL, START]:
            game_map[0][col] = TERMINAL
            break
    return game_map


if __name__ == "__main__":
    game_map = generate()
    print("\n".join(str(row) for row in game_map))
