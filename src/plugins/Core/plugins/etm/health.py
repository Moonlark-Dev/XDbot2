from .._utils import *
from ..duel import monomer


def get_max_hp(user_id: int) -> int:
    return int(get_data(user_id, "health"))


def get_data(user_id: int, key: str) -> any:
    return int(
        monomer.Monomer(
            (user_data := Json(f"duel/u{user_id}.json")).get(
                "weapons", "leather_case"
            ),
            user_data.get("realics", {}),
            user_data.get("ball", "leather_case"),
            100,
            f"u{user_id}",
            user_data.get("weapons_level", 1),
            user_data.get("ball_level", 1),
        ).data[key]
    )
