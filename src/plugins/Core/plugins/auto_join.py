from nonebot import on_type
from nonebot.adapters.onebot.v11 import Bot
from . import _error
import traceback
from nonebot.adapters.onebot.v11.event import GroupRequestEvent
from .accout import reloadMuiltData

@on_type(GroupRequestEvent).handle()
async def group_request_handle(
        bot: Bot,
        event: GroupRequestEvent):
    try:
        if event.sub_type == "invite":
            await _error.report((
                "「被邀请加群」\n"
                f"群号：{event.group_id}\n"
                f"用户：{event.user_id}"))
            await event.approve(bot)
            await reloadMuiltData()

    except BaseException:
        await _error.report(traceback.format_exc())
