from .etm import bag
from ..plugins._utils import *
from .etm import economy
from .duel.monomer import load_json
import os
import os.path
import random


def random_a_level() -> int:
    """
    随机一个出货的等级

    Returns:
        int: 等级
    """
    number = random.random()
    if number <= 0.4:
        return 0
    elif number <= 0.65:
        return 1
    elif number <= 0.8:
        return 2
    elif number <= 0.9:
        return 3
    elif number <= 0.96:
        return 4
    else:
        return 5


def random_type() -> str:
    """
    随机装备类型

    Returns:
        str: 装备类型，`weapons`或`ball`
    """
    if random.random() <= 0.75:
        return "weapons"
    return "ball"


def get_kits_by_level(level: int) -> list:
    """
    根据等级获取对应的套装

    Args:
        level (int): 等级

    Returns:
        list: 套装列表
    """
    kit_list = []
    for file in os.listdir("src/plugins/Core/duel/kits"):
        if file.endswith(".json"):
            data = load_json(f"kits/{file}")
            data["id"] = file.replace(".json", "")
            if data["level"] == level:
                kit_list.append(data)
    return kit_list


def make_wish(user_id: str) -> dict:
    """
    生成祈愿

    Args:
        user_id (str): 用户 ID

    Returns:
        str: 祈愿结果
    """
    level = random_a_level()
    kits = get_kits_by_level(level)
    if len(kits) == 0:
        return make_wish(user_id)
    kit = random.choice(kits)
    _type = random_type()
    bag.add_item(user_id, _type, 1, {"kit": kit["id"], "level": 1})
    return {"kit": kit, "type": _type}


def get_wish_count(user_id: str) -> int:
    """
    获取用户祈愿次数

    Args:
        user_id (str): 用户 ID

    Returns:
        int: 祈愿次数
    """
    data = Json("wish.data.json")
    data[user_id] = data.get(user_id, 0) + 1
    return data[user_id]


@create_command("wish")
async def handle_wish_command(bot: Bot, event: MessageEvent, message: Message) -> None:
    if not economy.use_vimcoin(event.user_id, 160):
        await finish("currency.no_money", [160], event.user_id)
    data = make_wish(str(event.user_id))
    await finish(
        "wish.result",
        [
            get_wish_count(str(event.user_id)),
            "⭐" * (data["kit"]["level"] + 1),
            data["kit"][data["type"]]["name"],
            lang.text(f"wish.type_{data['type']}", [], event.user_id),
        ],
        event.user_id,
        False,
        True,
    )


# [HELPSTART] Version: 2
# Command: wish
# Msg: 祈愿
# Info: 进行一次祈愿
# Usage: wish
# [HELPEND]
