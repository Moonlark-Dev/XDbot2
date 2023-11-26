from typing import Any
from nonebot.adapters.onebot.v11 import Bot
from nonebot import get_bots
from nonebot import get_driver
from nonebot.exception import ActionFailed, MockApiException


async def on_called_api(
        bot: Bot,
        exception: Exception | None,
        api: str,
        data: dict[str, Any],
        result: dict[str, Any]
):
    if not exception:
        return
    # print(locals())
    if not isinstance(exception, ActionFailed):
        return
    if not data.get("__retry__", True):
        return
    for b in get_bots().values():
        try:
            data["__retry__"] = False
            raise MockApiException(await b.call_api(api, **data))
        except ActionFailed as e:
            continue

@get_driver().on_bot_connect
async def _(bot: Bot):
    bot.on_called_api(on_called_api)
        

