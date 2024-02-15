from map import generate
from search import search

game_map = generate()
print("Map:")
print("\n".join(str(row) for row in game_map))

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

import copy
print("\nSteps (MIN):")
print(search(copy.deepcopy(game_map)))

from image import generate

generate(game_map)


