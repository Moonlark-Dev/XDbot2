import base64
from typing import Optional, cast
from nonebot import get_driver
from ._utils import *
from nonebot.adapters import Bot as BaseBot
from nonebot.exception import MockApiException
from .account import get_accounts_data


class GroupNotFoundException(Exception):
    pass


def select_bot_by_group_id(group_id: int) -> Optional[Bot]:
    """
    使用群号获取 Bot 对象

    Args:
        group_id (int): 群号

    Returns:
        Optional[Bot]: Bot 对象, 查找失败则返回 None
    """
    return get_accounts_data().get(group_id)


async def check_group_id(bot: Bot, api: str, data: dict) -> None:
    """
    检查并修复 API 调用中的群号

    Args:
        bot (Bot): 对应 Bot
        api (str): API 终结点
        data (dict): 调用参数

    Raises:
        MockApiException: 阻止 API 调用
    """
    if "group_id" not in data.keys():
        return
    groups = await bot.get_group_list()
    for group in groups:
        if group["group_id"] == int(data["group_id"]):
            return
    group_id = int(data["group_id"])
    if correct_bot := select_bot_by_group_id(group_id):
        raise MockApiException(await correct_bot.call_api(api, **data))
    raise GroupNotFoundException(f"区域外的群号: {group_id}")


def check_message_images(original_message: Message) -> Message:
    message = original_message.copy()
    length = -1
    for segment in message:
        length += 1
        if segment.type != "image":
            continue
        file = cast(str, segment.data.get("file", ""))
        if not file.startswith("file://"):
            continue
        with open(file[7:], "rb") as f:
            data = base64.b64encode(f.read()).decode("utf-8")
        message[length].data["file"] = f"base64://{data}"
    return message


async def on_calling_api(bot: BaseBot, api: str, data: dict) -> None:
    if not isinstance(bot, Bot):
        return
    await check_group_id(bot, api, data)
    if "message" in data.keys() and isinstance(data["message"], Message):
        data["message"] = check_message_images(data["message"])


@get_driver().on_bot_connect
async def _(bot: Bot) -> None:
    """
    注册调用接口前钩子函数

    Args:
        bot (Bot): Bot
    """
    bot.on_calling_api(on_calling_api)
