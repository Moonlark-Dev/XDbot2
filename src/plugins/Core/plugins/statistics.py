import nonebot
from nonebot.adapters.onebot.v11 import MessageEvent
from nonebot.matcher import Matcher
from . import _error as error
from . import _lang as lang
import traceback
import json
import os
import os.path

def get_lines(top = "./src/plugins/Core"):
    lines = 0
    for file in os.listdir(top):
        if os.path.isfile(os.path.join(top, file)):
            try:
                with open(os.path.join(top, file), encoding="utf-8") as f:
                    lines += f.read().splitlines().__len__()
            except:
                pass
        else:
            lines += get_lines(os.path.join(top, file))
    return lines

@nonebot.on_command("statistics").handle()
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
                    group_member_count += (await bot.get_group_info(group_id=group["group_id"]))["member_count"]

        friends = []
        for bot in bots:
            for friend in await bot.get_friend_list():
                if friend["user_id"] not in friends:
                    friends.append(friend["user_id"])

        await matcher.finish(lang.text("statistics.info", [
            len(groups),
            group_member_count,
            friends,
            get_lines()
        ], event.get_user_id()))
                    
            
    except:
        await error.report(traceback.format_exc(), matcher)
