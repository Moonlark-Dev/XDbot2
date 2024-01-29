from .._utils import *
from .duel.entity.user import User


def get_max_hp(user_id: int) -> int:
    return User(str(user_id)).max_hp


def get_data(user_id: int, key: str) -> Any: ...
