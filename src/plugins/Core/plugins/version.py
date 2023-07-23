import traceback
from nonebot import on_command
import os
from ._utils import Json, lang
from . import _error as error
from nonebot.matcher import Matcher


@on_command("version", aliases={"版本信息"}).handle()
async def show_version(matcher: Matcher):
    try:

        git_log = os.popen(
            r"git log --pretty=format:%B").read().splitlines()[0]
        await matcher.finish(lang.text("version.version", [Json("init.json")["version"], git_log]))
    except BaseException:
        await error.report(traceback.format_exc(), matcher)
