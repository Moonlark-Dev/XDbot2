import traceback
from nonebot import on_command
import os
from . import _error as error
from nonebot.matcher import Matcher

git_log = os.popen("git log").read()

@on_command("version", aliases={"版本信息"}).handle()
async def show_version(matcher: Matcher):
    try:
        await matcher.finish(git_log.split("\n\n")[0])
    except BaseException:
        await error.report(traceback.format_exc(), matcher)

