from .email import send_email
from nonebot_plugin_apscheduler import scheduler
import math
from nonebot import require
from ._utils import *
import os
import time

require("nonebot_plugin_apscheduler")


@scheduler.scheduled_job("cron", hour="0", minute="0", second="0", id="reset_point")
async def reset_point():
    users = []
    for user in get_quickmath_user_list():
        users.append(
            {
                "user_id": user,
                "points": Json(f"quickmath/u{user}.json").get("points", 0),
            }
        )
    users = assign_rewards(
        assign_ranks(sorted(users, key=lambda x: x["points"], reverse=True))
    )
    for user in users:
        await send_email(
            user["user_id"],
            lang.text("quickmath_points.email_title", [], user["user_id"]),
            lang.text(
                "quickmath_points.email_text",
                [
                    time.strftime("%Y/%m/%d", time.localtime(time.time() - 43200)),
                    user["points"],
                    user["ranking"],
                ],
                user["user_id"],
            ),
            [
                {"id": "vimcoin", "count": user["rewards"]["vimcoin"], "data": {}},
                {"id": "exp", "count": user["rewards"]["exp"], "data": {}},
            ],
        )
        Json(f"quickmath/u{user['user_id']}.json")["points"] = 0
    Json(f"quickmath/global.json")["count"] = 0


def assign_rewards(
    ranked_users: list[dict[str, str | int | dict]]
) -> list[dict[str, str | int | dict]]:
    answered_count = Json(f"quickmath/global.json").get("count", 0)
    user_list = ranked_users.copy()
    for i in range(len(user_list)):
        user = user_list[i]
        user["rewards"] = {"vimcoin": answered_count * 4, "exp": answered_count * 4}
    for i in range(math.ceil(len(user_list) * 0.75)):
        user = user_list[i]
        user["rewards"]["vimcoin"] += answered_count * 3
        user["rewards"]["exp"] += answered_count * 3
    for i in range(math.ceil(len(user_list) * 0.5)):
        user = user_list[i]
        user["rewards"]["vimcoin"] += answered_count * 3
        user["rewards"]["exp"] += answered_count * 2
    for i in range(math.ceil(len(user_list) * 0.25)):
        user = user_list[i]
        user["rewards"]["vimcoin"] += answered_count * 2
        user["rewards"]["exp"] += answered_count * 1
    return user_list


def get_quickmath_user_list() -> list[str]:
    user_list = []
    try:
        for file in os.listdir("data/quickmath"):
            if file.startswith("u") and file.endswith(".json"):
                if Json(f"quickmath/{file}")["points"]:
                    user_list.append(file[1:-5])
    except OSError:
        pass
    return user_list


def assign_ranks(users: list[dict[str, str | int]]) -> list[dict[str, str | int]]:
    currect_ranking = 0
    currect_minimum_pints = 1145141919810
    ranked_users = []
    for user in users:
        if user["points"] < currect_minimum_pints:
            currect_ranking += 1
            currect_minimum_pints = user["points"]
        ranked_users.append(
            {
                "user_id": user["user_id"],
                "points": user["points"],
                "ranking": currect_ranking,
            }
        )
    return ranked_users


def format_time(seconds):
    h = int(seconds / 3600)
    m = int(seconds / 60) % 60
    return f"{h}:{m}'"


def search_user_in_ranking(
    user_id: str, ranked_users: list[dict[str, str | int]]
) -> dict[str, str | int | None]:
    for user in ranked_users:
        if user_id == user["user_id"]:
            return user
    return {"user_id": user_id, "points": 0, "ranking": 999}


@create_command("qm-point", aliases={"quick-math-point", "qm-p", "qm-pr"})
async def handle_qm_point_command(
    bot: Bot, event: MessageEvent, _message: Message, matcher: Matcher = Matcher()
) -> None:
    users = []
    for user in get_quickmath_user_list():
        users.append(
            {
                "user_id": user,
                "points": Json(f"quickmath/u{user}.json").get("points", 0),
            }
        )
    users = assign_ranks(sorted(users, key=lambda x: x["points"], reverse=True))
    reply_text = lang.text(
        "quickmath_points.ranking_title",
        [
            format_time(
                int((int((time.time()) / 86400) + 1) * 86400 - 28800 - time.time())
            )
        ],
        event.user_id,
    )
    for user in users[:13]:
        reply_text += lang.text(
            "quickmath_points.ranking_item",
            [
                user["ranking"],
                (await bot.get_stranger_info(user_id=int(user["user_id"])))["nickname"],
                user["points"],
            ],
            event.user_id,
        )
    reply_text += lang.text("sign.hr", [], event.user_id) + "\n"
    reply_text += lang.text(
        "quickmath_points.ranking_item",
        [
            (user := search_user_in_ranking(event.get_user_id(), users))["ranking"],
            event.sender.nickname,
            user["points"],
        ],
        event.user_id,
    )
    await matcher.finish(reply_text)
