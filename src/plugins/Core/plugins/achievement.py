from . import _error as error
import json
from traceback import format_exc
from nonebot import on_command
from nonebot.adapters.onebot.v11 import Message, MessageEvent
from nonebot.matcher import Matcher
from nonebot.params import CommandArg
from .etm import achievement
from . import _lang as lang


@on_command("achievement", aliases={"成就", "achi"}).handle()
async def show_achievement(matcher: Matcher,
                           event: MessageEvent,
                           message: Message = CommandArg()):
    try:
        argv = str(message).split(" ")
        if argv[0] in ["list", "列表", ""]:
            data = achievement.get_user_achievement(event.get_user_id())
            reply = lang.text("achi.title", [], event.get_user_id())
            length = 1
            for item in data:
                reply += f"\n{length}. {item}"
                length += 1
            await matcher.finish(reply)
        elif argv[0] in ["view", "show", "查看"]:
            achi_data = achievement.ACHIEVEMENTS[" ".join(argv[1:])]
            if achi_data["name"] in achievement.get_user_achievement(
                    event.get_user_id()):
                unlck_status = lang.text("achi.unlocked", [],
                                         event.get_user_id())
            elif achievement.get_unlck_progress(achi_data['name'],
                                                event.get_user_id()):
                unlck_status = f"{achievement.get_unlck_progress(achi_data['name'], event.get_user_id())} / {achi_data['need_progress']} {(achievement.get_unlck_progress(achi_data['name'], event.get_user_id()) / achi_data['need_progress']) * 100}%"
            else:
                unlck_status = lang.text("achi.locked", [],
                                         event.get_user_id())
            await matcher.finish(
                lang.text("achi.info", [
                    achi_data['name'], achi_data['condition'], unlck_status
                ], event.get_user_id()) +
                (f"\n{achi_data['info']}" if 'info' in achi_data.keys() else ''
                 ))
        # elif argv[0] in ["all", "全部"]:
        #     reply = lang.text("achi.title_all", [], event.get_user_id())
        #     length = 1
        #     for item in list(achievement.ACHIEVEMENTS.values()):
        #         reply += f"\n{length}. {item['name']}"
        #         length += 1
#             await matcher.finish(reply)
    except BaseException:
        await error.report(format_exc(), matcher)


# [HELPSTART] Version: 2
# Command: achievement
# Usage: achievement [list]
# Usage: achievement view <成就名>
# Msg: 查看成就
# Info: 查看成就
# [HELPEND]
