from ._utils import *
from nonebot_plugin_apscheduler import scheduler
import math

def calculate_distance(user_id: str | int, target: tuple[int, int]) -> float:
    user_pos = (
        Json(f"data/adventure/users/{user_id}.json").get("x", 0),
        Json(f"data/adventure/users/{user_id}.json").get("y", 0)
    )
    return math.sqrt(
        (user_pos[0] - target[0]) ** 2 + 
        (user_pos[1] - target[1]) ** 2
    )
    

@scheduler.scheduled_job("corn", minute="*")
async def add_stamina():
    os.makedirs("data/adventure/users", exist_ok=True)
    for user in os.listdir("data/adventure/users"):
        if Json(f"data/adventure/users/{user}").get("stamina", 0) >= 1440:
            continue
        Json(f"data/adventure/users/{user}")["stamina"] += 1
        if calculate_distance(user[:-5], (0, 0)) <= 100:
            Json(f"data/adventure/users/{user}")["stamina"] += 2

