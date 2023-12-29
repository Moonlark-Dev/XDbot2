from typing import Literal, Optional, TypedDict, cast
from ._utils import *
from nonebot_plugin_apscheduler import scheduler
import math
from .etm import health
import asyncio

# class Event(TypedDict):
#     type: Literal[
#         "update_time"
#     ]
#     data: dict[str, Any]

# event_list: list[Event] = []

@create_command("init-adventure", permission=SUPERUSER)
async def _(bot: Bot, event: MessageEvent, message: Message) -> None:
    for file in os.listdir("data/adventure/map"):
        os.remove(os.path.join("data/adventure/map", file))
    block_0 = Json("adventure/map/block_0_0.json")

def get_user_stamina(user_id: str | int) -> int:
    return Json(f"data/adventure/users/{user_id}.json").get("stamina", 1440)

def get_pos(user_id: str | int) -> tuple[int, int]:
    return (
        Json(f"data/adventure/users/{user_id}.json").get("x", 0),
        Json(f"data/adventure/users/{user_id}.json").get("y", 0)
    )

def calculate_distance(pos_1: tuple[int, int], pos_2: tuple[int, int]) -> float:
    return math.sqrt(
        (pos_1[0] - pos_2[0]) ** 2 + 
        (pos_1[1] - pos_2[1]) ** 2
    )

def compute_user_to_point_distance(user_id: str | int, target: tuple[int, int]) -> float:
    user_pos = get_pos(user_id)
    return calculate_distance(user_pos, target)

@scheduler.scheduled_job("cron", minute="*")
async def add_stamina():
    os.makedirs("data/adventure/users", exist_ok=True)
    for user in os.listdir("data/adventure/users"):
        if Json(f"data/adventure/users/{user}").get("stamina", 1440) >= 1440:
            continue
        Json(f"data/adventure/users/{user}")["stamina"] += 1
        if compute_user_to_point_distance(user[:-5], (0, 0)) <= 100:
            Json(f"data/adventure/users/{user}")["stamina"] += 2

@create_command("adventure", {"ad", "duel-a"})
async def handle_adventure_command(bot: Bot, event: MessageEvent, message: Message):
    args = message.extract_plain_text().split(" ")
    match args[0]:

        case _:
            await finish(
                "adventure.user_info",
                [
                    get_pos(event.user_id),
                    get_user_stamina(event.user_id),
                    1440,
                    health.get_data(event.user_id, "health"),
                    health.get_max_hp(event.user_id)
                ],
                event.user_id,
                False,
                True
            )

def get_block_id(pos: tuple[int, int]) -> str:
    return "_".join([
        str(int((pos[0] + 16) / 32)),
        str(int((pos[1] + 16) / 32))
    ])

def get_block_center(block_id: str) -> tuple[int, int]:
    block_id_split = block_id.split("_")
    block_pos = int(block_id_split[0]), int(block_id_split[1])
    return block_pos[0] * 32 + 16, block_pos[1] * 32 + 16
    

def get_block_data(block_id: str) -> Json:
    data = Json(f"adventure/map/block_{block_id}.json")
    if not data.to_dict():
        data.update({
            "center": get_block_center(block_id),
            "items": [],
            "protected": False
        })
    return data

def generate_square_points(center: tuple[int, int], side_length: int):
    # 计算正方形的半边长
    half_side = side_length // 2
    # 生成正方形的四个边上的点
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


def get_outer_blocks(center: tuple[int, int], radius: int) -> set:
    center_block = cast(
        tuple[int,int],
        tuple([int(i) for i in get_block_id(center).split("_")])
    )
    blocks = set()
    for b in generate_square_points(center_block, radius):
        blocks.add(f"{b[0]}_{b[1]}")
    return blocks


def find_teleportation_point(user_id: str | int, pos: tuple[int, int], max_distance: int):
    nearest_teleportation_point: Optional[dict[str, Any]] = None
    radius = 0
    while not nearest_teleportation_point:
        for block_id in get_outer_blocks(pos, radius):
            block = get_block_data(block_id)
            # print(block["center"], block_id)
            if calculate_distance(block["center"], pos) >= max_distance * 32:
                break
            for item in block["items"]:
                if calculate_distance(item["pos"], pos) > max_distance:
                    continue
                if item["type"].endswith("teleportation_point"):
                    # TODO 权限校验
                    if (not nearest_teleportation_point)\
                        or calculate_distance(nearest_teleportation_point["pos"], pos) \
                            > calculate_distance(item["pos"], pos):
                        nearest_teleportation_point = item
        else:
            radius += 1
            continue
        break
    return nearest_teleportation_point


# async def move(user_id: str | int, target_pos: tuple[int, int]) -> None:
#     nearest_teleportation_point = find_teleportation_point(
#         user_id,
#         target_pos, 
#         int(
#             compute_user_to_point_distance(user_id, target_pos) / 2 / 32
#         )
#     )
#     # print(nearest_teleportation_point)
#     if nearest_teleportation_point is not None and 40 + calculate_distance(nearest_teleportation_point["pos"], target_pos) >= compute_user_to_point_distance(user_id, target_pos):
#         nearest_teleportation_point = None
#     if nearest_teleportation_point is not None:
#         need_stamina = 40 + calculate_distance(nearest_teleportation_point["pos"], target_pos)
#     else:
#         need_stamina = compute_user_to_point_distance(user_id, target_pos)
#     if need_stamina > get_stamina(user_id):
#         await finish("adventure.no_stamina_to_move", [get_stamina(user_id), need_stamina], user_id)
#     data = Json(f"data/adventure/users/{user_id}.json")
#     data["x"], data["y"] = target_pos
#     data["stamina"] -= need_stamina
#     await finish("currency.ok", [get_stamina(user_id), need_stamina], user_id)
    



# @create_command("move", {"goto", "duel-m"})
# async def handle_move_command(bot: Bot, event: MessageEvent, message: Message) -> None:
#     args = message.extract_plain_text().split(" ")
#     if not (len(args) == 2 or len(args) == 0):
#         await finish("currency.wrong_argv", ["move"], event.user_id)
#     elif len(args) == 0:
#         args = [0, 0]
#     args = cast(tuple[int, int], tuple([int(i) for i in args]))
#     await move(event.user_id, args)