import traceback
from nonebot import on_command
import json

from nonebot.adapters.onebot.v11 import MessageEvent
from . import _error, _lang
from nonebot.matcher import Matcher


@on_command("qm-avg").handle()
async def qmavg(matcher: Matcher, event: MessageEvent):
    try:
        data = json.load(
            open("data/quick_math.average.json", encoding="utf-8"))
        await matcher.send(_lang.text("qm_avg.info", [data["average"]], event.get_user_id()))
    except:
        await _error.report(traceback.format_exc(), matcher)

# [HELPSTART] Version: 2
# Command: qm-avg
# Info: 速算平均用时
# Usage: qm-avg
# [HELPEND]
