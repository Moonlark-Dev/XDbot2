from .map import generate
from .search import search
from .argv import ARGUMENTS

difficulty = "normal"

# game_map = generate(**ARGUMENTS[difficulty]["map"])
# print("Map:")
# print("\n".join(str(row) for row in game_map))

game_map = [
    [1, 1, 1, 1, 1, 1, 1, 3, 1, 1, 1, 1],
    [1, 5, 2, 0, 7, 0, 0, 0, 2, 0, 0, 1],
    [1, 0, 7, 0, 0, 0, 0, 5, 1, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 7, 5, 0, 0, 1],
    [1, 7, 2, 0, 0, 2, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 7, 0, 0, 1],
    [1, 0, 1, 0, 0, 2, 0, 5, 0, 1, 0, 1],
    [1, 0, 4, 2, 0, 0, 7, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
]

# game_map = [
#     [1, 1, 1, 3, 1, 1, 1, 1],
#     [1, 0, 0, 0, 2, 4, 1, 1],
#     [1, 0, 0, 1, 0, 1, 2, 1],
#     [1, 1, 0, 0, 0, 0, 0, 1],
#     [1, 0, 0, 0, 0, 0, 0, 1],
#     [1, 1, 1, 1, 1, 1, 1, 1]
# ]

# game_map = [
#     [1, 1, 1, 1, 1, 3, 1, 1],
#     [1, 0, 0, 0, 0, 0, 2, 1],
#     [1, 0, 0, 0, 0, 0, 0, 1],
#     [1, 0, 0, 0, 0, 0, 0, 1],
#     [1, 0, 4, 0, 0, 0, 0, 1],
#     [1, 1, 1, 1, 1, 1, 1, 1]
# ]

# game_map = [
# [1, 1, 1, 3, 1, 1, 1, 1],
# [1, 0, 2, 0, 0, 4, 0, 1],
# [1, 0, 0, 0, 0, 0, 0, 1],
# [1, 1, 0, 0, 0, 0, 0, 1],
# [1, 0, 0, 0, 0, 0, 1, 1],
# [1, 1, 1, 1, 1, 1, 1, 1]
# ]


from .image import generateImage

generateImage(game_map)

import copy

print("\nSteps (MIN):")
print(search(copy.deepcopy(game_map), **ARGUMENTS[difficulty]["search"]))
