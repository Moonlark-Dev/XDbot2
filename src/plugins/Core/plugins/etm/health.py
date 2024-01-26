from .._utils import *



def get_max_hp(user_id: int) -> int:
    return int(get_data(user_id, "health"))


def get_data(user_id: int, key: str) -> Any:
    ...
