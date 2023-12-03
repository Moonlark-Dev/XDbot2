import math
from ._utils import *
from typing import (
    Optional,
    TypedDict,
    Literal,
    cast
)

class Item(TypedDict):
    item_id: int
    pos: tuple[int, int]
    data: dict[str, Any]

class Buff(TypedDict):
    buff_id: int
    start_time: float
    duration: int

class Entity(TypedDict):
    entity_id: str
    pos: tuple[int, int]
    buff: list[Buff]

class Block(TypedDict):
    block_pos: tuple[int, int]
    items: list[Item]
    entities: list[Entity]
    data: dict[str, Any]

class Event(TypedDict):
    subject: Optional[str]
    type: Literal[
        "move",
        "teleport",
        "die",
        "rebirth"
    ]
    data: dict[str, Any]

loaded_blocks: dict[str, Block] = {}

def get_item_info(item_id: int) -> dict[str, str | int | dict]:
    """
    获取物品信息

    Args:
        item_id (int): 物品ID

    Returns:
        dict[str, str | int | dict]: 物品信息
    """
    return json.load(open(f"src/plugins/Core/plugins/adventure/items/{item_id}.json", encoding="utf-8"))

def create_item(item_id: int, pos: tuple[int, int], **kwargs) -> Item:
    """
    创建物品

    Args:
        item_id (int): 物品ID
        pos (tuple[int, int]): 位置

    Returns:
        Item: 物品对象
    """
    data = cast(dict[str, Any], get_item_info(item_id).get("data", {}))
    data.update(kwargs)
    return {
        "item_id": item_id,
        "data": data,
        "pos": pos
    }

def retrieve_peripheral_blocks(center: tuple[int, int], side_length: int) -> list[tuple[int, int]]:
    """
    获取区块外围区块相对位置

    Args:
        center (tuple[int, int]): 中心区块相对位置
        side_length (int): 范围 (单位：区块)

    Returns:
        list[tuple[int, int]]: 外围区块列表
    """
    half_side = side_length // 2
    edge_points = [
        (center[0], center[1] + half_side),
        (center[0] + half_side, center[1]),
        (center[0], center[1] - half_side),
        (center[0] - half_side, center[1])
    ]
    corner_points = [
        (center[0] + half_side, center[1] + half_side),
        (center[0] - half_side, center[1] + half_side),
        (center[0] - half_side, center[1] - half_side),
        (center[0] + half_side, center[1] - half_side)
    ]
    all_points = list(set(edge_points + corner_points))
    return all_points

def clear_loaded_blocks() -> None:
    """
    清理已加载的区块
    """
    block_code_to_remove: list[str] = []
    for block_code, block in loaded_blocks.items():
        if block["data"].get("keep_loading"):
            continue
        for entity in block["entities"]:
            if get_entity_type_by_id(entity["entity_id"]) == "user":
                break
        else:
            block_code_to_remove.append(block_code)
    for block_code in block_code_to_remove:
        loaded_blocks.pop(block_code)

def calculate_distance(pos_1: tuple[int, int], pos_2: tuple[int, int]) -> float:
    """
    计算点到点的距离

    Args:
        pos_1 (tuple[int, int]): 坐标1
        pos_2 (tuple[int, int]): 坐标2

    Returns:
        float: 距离
    """
    return math.sqrt(
        (pos_1[0] - pos_2[0]) ** 2 + 
        (pos_1[1] - pos_2[1]) ** 2
    )

# def is_pos_protected(pos: tuple[int, int]) -> bool:
#     blocks_to_check: list[tuple[int, int]] = []
#     for i in [1,2,3]:
#         blocks_to_check += retrieve_peripheral_blocks(get_block_pos(pos), i)
#     for block_pos in blocks_to_check:
#         block = get_block_data(get_block_code(block_pos))
#         for item in block["items"]:

def is_location_protected(pos: tuple[int, int]) -> None | dict[str, dict[str, bool]]:
    """
    检查位置是否被保护

    Args:
        pos (tuple[int, int]): 坐标

    Returns:
        None | dict[str, dict[str, bool]]: 如果被保护, 将返回权限信息; 未被保护则返回 None
    """
    blocks_to_check: list[tuple[int, int]] = []
    for i in [1,2,3]:
        blocks_to_check += retrieve_peripheral_blocks(get_block_pos(pos), i)
    for block_pos in blocks_to_check:
        block = get_block_data(get_block_code(block_pos))
        for item in block["items"]:
            if "__protect__" in item["data"]:
                if calculate_distance(pos, item["pos"]) <= item["data"]["__protect__"]["zone"]:
                    return item["data"]["__protect__"]["permission"]

def get_entity_type_by_id(entity_id: str) -> str:
    """
    获取实体类型

    Args:
        entity_id (str): 实体ID

    Returns:
        str: 实体类型
    """
    return entity_id.split("_")[0] or "_"

def get_permission(_permission: dict[str, dict[str, bool]], entity_id: str) -> dict[str, bool]:
    """
    解析获取实体权限

    Args:
        _permission (dict[str, dict[str, bool]]): 原权限表
        entity_id (str): 实体ID

    Returns:
        dict[str, bool]: 权限列表
    """
    permission: dict[str, bool] = _permission.get("@_", {})
    permission.update(_permission.get(
        f"@{get_entity_type_by_id(entity_id)}",
        {}
    ))
    permission.update(_permission.get(
        entity_id,
        {}
    ))
    return permission

def is_location_moveable(pos: tuple[int, int], entity_id: str) -> bool:
    """
    位置是否可移动

    Args:
        pos (tuple[int, int]): 位置
        entity_id (str): 实体ID

    Returns:
        bool: 是否可移动
    """
    for block in get_block_data(get_block_code(get_block_pos(pos)))["items"]:
        if block["pos"] == pos:
            return False
    if not (protect_permission := is_location_protected(pos)):
        return True
    permission: dict[str, bool] = get_permission(protect_permission, entity_id)
    return permission.get("moveable", True)

@create_command("init-adventure", permission=SUPERUSER)
async def _(bot: Bot, event: MessageEvent, message: Message) -> None:
    loaded_blocks.clear()
    os.rmdir("data/ad")
    block = init_block(
        get_block_pos(
            (0,0)
        ),
        [
            create_item(
                0,
                (0,0),
                display_name="中心",
                need_unlock=False,
                __protect__={
                    "zone": 64,
                    "permission": {
                        "@_": {
                            "editable": False,
                            "moveable": False
                        },
                        "@user": {
                            "moveable": True
                        }
                    }
                }
            )
        ],
        keep_loading=True
    )
    loaded_blocks[get_block_code(block["block_pos"])] = block

def init_block(block_pos: tuple[int, int], items: list[Item] = [], entities: list[Entity] = [], **kwargs) -> Block:
    """
    初始化区块

    Args:
        block_pos (tuple[int, int]): 区块相对坐标
        items (list[Item], optional): 物品列表. Defaults to [].
        entities (list[Entity], optional): 实体列表. Defaults to [].

    Returns:
        Block: 区块数据
    """
    block_data = Json(f"ad/blocks/{get_block_code(block_pos)}.json")
    block_data.update({
        "block_pos": block_pos,
        "items": items,
        "entities": entities,
        "data": kwargs
    })
    return cast(Block, block_data)

def _load_block_data(block_code: str) -> Block:
    """
    加载区块数据

    Args:
        block_code (str): 区块代码

    Returns:
        Block: 区块数据
    """
    if not os.path.isfile(f"data/ad/blocks/{block_code}.json"):
        return init_block(get_block_pos_by_code(block_code))
    return cast(Block, Json(f"ad/blocks/{block_code}.json"))

def get_block_data(block_code: str) -> Block:
    """
    获取区块数据 (允许Loaded)

    Args:
        block_code (str): 区块代码

    Returns:
        Block: 区块数据
    """
    return loaded_blocks.get(block_code, _load_block_data(block_code))

def get_block_pos_by_code(block_code: str) -> tuple[int, int]:
    """
    通过区块代码获取区块相对坐标

    Args:
        block_code (str): 区块代码

    Returns:
        tuple[int, int]: 区块相对坐标
    """
    p = block_code.split("_")
    return int(p[0]), int(p[1])

def get_block_pos(pos: tuple[int, int]) -> tuple[int, int]:
    """
    获取坐标所在区块相对位置

    Args:
        pos (tuple[int, int]): 坐标

    Returns:
        tuple[int, int]: 所在区块相对位置
    """
    return int((pos[0] + 16) / 32), int((pos[1] + 16) / 32)

def get_block_code(block_pos: tuple[int, int]) -> str:
    """
    通过相对位置获取区块代码

    Args:
        block_pos (tuple[int, int]): 区块相对位置

    Returns:
        str: 区块代码
    """
    return f"{block_pos[0]}_{block_pos[1]}"

def handle_event(event: Event) -> None:
    """
    处理事件

    Args:
        event (Event): 事件信息
    """


def create_event_data(
        type: Literal[
            "move",
            "teleport",
            "die",
            "rebirth"
        ],
        subject: Optional[str] = None,
        data: dict[str, Any] = {}
) -> Event:
    """
    创建事件数据

    Args:
        type (Literal[ &quot;move&quot;, &quot;teleport&quot;, &quot;die&quot;, &quot;rebirth&quot; ]): 事件类型
        subject (Optional[str], optional): 事件主体. Defaults to None.
        data (dict[str, Any], optional): 事件数据. Defaults to {}.

    Returns:
        Event: 事件数据
    """
    return {
        "type": type,
        "subject": subject,
        "data": data
    }

def create_event(
        _type: Literal[
            "move",
            "teleport",
            "die",
            "rebirth"
        ],
        subject: Optional[str] = None,
        **kwargs
) -> None:
    """
    创建事件

    Args:
        _type (Literal[ &quot;move&quot;, &quot;teleport&quot;, &quot;die&quot;, &quot;rebirth&quot; ]): 事件类型
        subject (Optional[str], optional): 事件主体. Defaults to None.
    """
    handle_event(create_event_data(_type, subject, kwargs))

