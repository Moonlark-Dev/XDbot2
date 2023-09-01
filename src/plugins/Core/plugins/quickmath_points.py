from ._utils import *
import os
import time


def get_quickmath_user_list() -> list[str]:
    user_list = []
    try:
        for file in os.listdir("data/quickmath"):
            if file.startswith("u") and file.endswith(".json"):
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
    s = seconds % 60
    return f"{h}:{m}:{s}"


def search_user_in_ranking(
    user_id: str, ranked_users: list[dict[str, str | int]]
) -> dict[str, str | int | None]:
    for user in ranked_users:
        if user_id == user["user_id"]:
            return user
    return {"user_id": user_id, "points": 0, "ranking": 999}


@create_command("qm-point", aliases={"quick-math-point", "qm-p", "qm-pr"})
async def handle_qm_point_command(
    bot: Bot, event: MessageEvent, message: Message, matcher: Matcher = Matcher()
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
        [format_time(int((int((time.time()) / 86400) + 1) * 86400  - 28800 - time.time()))],
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
    reply_text += "\n" + lang.text("sign.hr", [], event.user_id) + "\n"
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
