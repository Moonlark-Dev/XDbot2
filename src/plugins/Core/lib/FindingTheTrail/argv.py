from .const import *

ARGUMENTS = {
    "easy": {
        "map": {"row": 6, "column": 8, "blocks": [(WALL, 2 / 15), (PISTON, 1 / 15)]},
        "search": {"max_step": 10},
        "min_step": 4,
    },
    "normal": {
        "map": {
            "row": 9,
            "column": 12,
            "blocks": [(WALL, 0.1), (PISTON, 0.1), (SAND, 0.1)],
        },
        "search": {"max_step": 15},
        "min_step": 4,
    },
}