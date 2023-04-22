import nonebot
from nonebot.adapters.onebot.v11 import MessageEvent
from nonebot.matcher import Matcher
from . import _error as error
from . import _lang as lang
import traceback
import os
import os.path

def get_lines(top = "./src/plugins/Core"):
    lines = 0
    chars = 0
    for file in os.listdir(top):
        if os.path.isfile(os.path.join(top, file)):
            try:
                with open(os.path.join(top, file), encoding="utf-8") as f:
                    code = f.read()
                    lines += code.splitlines().__len__()
                    chars += code.__len__()
            except:
                pass
        else:
            lines += get_lines(os.path.join(top, file))[0]
            chars += get_lines(os.path.join(top, file))[1]
    return lines, chars

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
            group_member_count,,
            get_lines()[0],
            get_lines()[1],
            len(friends)], event.get_user_id()))
                    
            
    except:
        await error.report(traceback.format_exc(), matcher)
