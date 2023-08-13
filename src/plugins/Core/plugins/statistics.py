import nonebot
from nonebot.adapters.onebot.v11 import MessageEvent
from nonebot.matcher import Matcher
from . import _error as error
from . import _lang as lang
import json
import traceback
import os
import os.path
from .etm import data as etmdata
import time

START_TIME = 1656345600


def get_run_time():
    t = time.time() - START_TIME
    return int(t / 86400)


def get_user_count():
    # count = 0
    # for file in os.listdir("data/etm"):
    #     if os.path.isdir(os.path.join("./data/etm", file)):
    #         try:
    #             int(file)
    #             count += 1
    #         except BaseException:
    #             pass
    # return count
    return len(list(etmdata.basic_data.keys()))


def get_lines(top="./src/plugins/Core"):
    lines = 0
    chars = 0
    for file in os.listdir(top):
        if os.path.isfile(os.path.join(top, file)):
            try:
                with open(os.path.join(top, file), encoding="utf-8") as f:
                    code = f.read()
                    lines += code.splitlines().__len__()
                    chars += code.__len__()
            except BaseException:
                pass
        else:
            lines += get_lines(os.path.join(top, file))[0]
            chars += get_lines(os.path.join(top, file))[1]
    return lines, chars


@nonebot.on_command("statistics", aliases={"统计信息"}).handle()
async def _(matcher: Matcher, event: MessageEvent):
    try:
        bots = list(nonebot.get_bots().values())

        groups = []
        group_member_count = 0
        for bot in bots:
            for group in await bot.get_group_list():
                if group["group_id"] in groups:
                    pass
                else:
                    groups.append(group["group_id"])
                    group_member_count += (
                        await bot.get_group_info(group_id=group["group_id"])
                    )["member_count"]

        friends = []
        for bot in bots:
            for friend in await bot.get_friend_list():
                if friend["user_id"] not in friends:
                    friends.append(friend["user_id"])

        await matcher.finish(
            lang.text(
                "statistics.info",
                [
                    get_user_count(),
                    len(groups),
                    group_member_count,
                    get_lines()[0],
                    get_lines()[1],
                    json.load(open("data/_error.count.json", encoding="utf-8"))[
                        "count"
                    ],
                    get_run_time(),
                ],
                event.get_user_id(),
            )
        )

    except BaseException:
        await error.report(traceback.format_exc(), matcher)
