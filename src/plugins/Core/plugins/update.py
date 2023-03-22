import os
from . import _lang as lang
from nonebot import on_command
from nonebot.matcher import Matcher
from nonebot.adapters.onebot.v11 import MessageEvent
from . import _error as error
import traceback


@on_command("update", aliases={"检查更新"}).handle()
async def update_xdbot(matcher: Matcher, event: MessageEvent):
    try:
        await matcher.send(lang.text("update.checking", [], event.get_user_id()))
        old_commit = os.popen("git log").read().split("\n")[
            0].split(" ")[1][:7]
        os.system("python3 update.py")
        await matcher.finish(
            lang.text(
                "update.finish",
                [old_commit, os.popen("git log").read().split("\n")[
                    0].split(" ")[1][:7]],
                event.get_user_id()))
    except:
        await error.report(traceback.format_exc(), matcher)
