from .map import generate
from .search import search
from .argv import ARGUMENTS

difficulty = "hard"

game_map = generate(**ARGUMENTS[difficulty]["map"])
print("Map:")
print("\n".join(str(row) for row in game_map))

# game_map = [
#     [1, 3, 1, 1],
#     [1, 8, 0, 1],
#     [1, 1, 8, 1],
#     [1, 0, 0, 1],
#     [1, 4, 0, 1],
#     [1, 1, 1, 1]
# ]

from .image import generateImage

generateImage(game_map, True)

import copy

print("\nSteps (MIN):")
print(search(copy.deepcopy(game_map), **ARGUMENTS[difficulty]["search"]))
