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
from ._utils import *

START_TIME = 1656345600


def get_run_time():
    t = time.time() - START_TIME
    return int(t / 86400)


def get_user_count():
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


from nonebot.matcher import matchers

# def get_commands() -> list[list[str]]:
#     commands = []
#     for matcher in matchers.provider[1]:
#         if matcher.type != "message" or not matcher.rule.checkers:
#             continue
#         if hasattr(list(matcher.rule.checkers)[0].call, "cmds"):
#             commands.append(list(matcher.rule.checkers)[0].call.cmds)
#     return commands

# @nonebot.get_driver().on_startup
# async def _() -> None:
#     Json("statistic.commands.ro.json")["commands"] = get_commands()

# def get_command_name(command_names: list[str]) -> str:
#     l = [cmd[0] for cmd in command_names]
#     return sorted(l, reverse=True, key=lambda x: ord(x))[0]

def get_command_name(rule: Rule) -> str:
    cmds = [[cmds[0] for cmds in checker.call.cmds] for checker in rule.checkers if hasattr(checker.call, "cmds")][0]
    return sorted(cmds, reverse=True)[0]

@create_message_handler_with_state()
async def _(bot: Bot, event: MessageEvent, message: Message, state: T_State) -> None:
    for matcher in matchers.provider[1]:
        if matcher.type != "message" or (not matcher.rule.checkers):
            continue
        if await matcher.check_rule(bot, event, state, None, None):
            command_name = get_command_name(matcher.rule)
            logger.info(f'命令 {command_name} 调用次数: {Json("statistic.commands.json").add(command_name, 1)}')
            return

@create_command("call-rank", {"指令调用排名", "command-rank"})
async def _(bot: Bot, event: MessageEvent, message: Message) -> None:
    data = sorted(Json("statistic.commands.json").items(), key=lambda x: x[1], reverse=True)
    total_count = 0
    for item in data:
        total_count += item[1]
    node = [lang.text("statistics.command_rank_title", [total_count], event.get_user_id())]
    length = 0
    for item in data:
        if length % 20 == 0:
            node.append("")
        else:
            node[-1] += "\n"
        node[-1] += lang.text(get_currency_key("rank_item"), [length := length + 1, item[0], item[1]], event.user_id)
    await send_node_message(bot, await generate_node_message(bot, node), event)

# [HELPSTART] Version: 2
# Command: call-rank
# Msg: 指令调用量排行
# Info: 指令调用量排行
# Usage: call-rank
# Command: statistics
# Msg: 统计信息
# Info: XDbot2 统计信息
# Usage: statistics
# [HELPEND]