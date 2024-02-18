from nonebot import on_regex
from .etm import (
    bag,
    economy,
    user
)
from .etm.item import Item
from ._utils import *

async def usePawCoin(user_id: str, count: int = 1) -> None:
    items: list[Item] = bag.get_user_bag(user_id)
    for i in range(len(items)):
        item = items[i]
        if item.item_id == "pawcoin":
            if item.count >= count:
                item.count -= count
                break
            else:
                count -= item.count
                item.count = 0
        if count == 0:
            break
    else:
        config = Json("pawcoin.config.json")[user_id]
        if user.get_user_data(user_id)["vimcoin"] >= count * 3 and config in [True, None]:
            economy.use_vi(user_id, count * 3)
        else:
            raise NoPawCoinException
