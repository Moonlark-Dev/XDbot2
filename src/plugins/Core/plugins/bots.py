from typing import Any
from nonebot.adapters.onebot.v11 import Bot
from nonebot import get_bots
from nonebot import get_driver
from nonebot.exception import ActionFailed, MockApiException


async def on_called_api(
        exception: Exception | None,
        api: str,
        data: dict[str, Any],
        result: dict[str, Any]
):
    if not exception:
        return
    if not isinstance(exception, ActionFailed):
        return
    if data.get("retry"):
        return
    for bot in get_bots().values():
        try:
            raise MockApiException(await bot.call_api(api, **data, retry=False))
        except ActionFailed:
            continue

@get_driver().on_bot_connect()
async def _(bot: Bot):
    await bot.on_called_api(on_called_api())
        

