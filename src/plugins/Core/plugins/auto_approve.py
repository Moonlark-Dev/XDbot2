from nonebot import get_driver, on_type
from nonebot.adapters.onebot.v11 import Bot
from . import _error
import traceback
from nonebot.adapters.onebot.v11.event import GroupRequestEvent
from . import _messenger

superusers = get_driver().config.superusers


@on_type(GroupRequestEvent).handle()
async def group_request_handle(
        bot: Bot,
        event: GroupRequestEvent):
    try:
        if event.sub_type == "invite":
            if event.get_user_id() in superusers:
                await event.approve(bot)
            else:
                _messenger.send_message(
                    f"温馨提示：请在 https://github.com/ITCraftDevelopmentTeam/XDbot2/issues/new?template=group.yml 发送一个入群申请来部署 XDbot2 到 {event.group_id}\n \n详细信息：\nhttps://github.com/ITCraftDevelopmentTeam/XDbot2/discussions/176",
                    event.get_user_id()
                )
                
    except BaseException:
        await _error.report(traceback.format_exc())
