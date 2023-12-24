import base64
from typing import Optional, cast
from nonebot import get_bots, get_driver
from ._utils import *
from nonebot.adapters import Bot as BaseBot
from nonebot.exception import MockApiException, ActionFailed, NetworkError
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


async def check_forward_node(bot: Bot, api: str, _data: dict) -> None:
    if (
        api not in ["send_group_forward_msg", "send_private_forward_msg"]
        or "__info_id__" in _data.keys()
        or len(bot.self_id) > 15
    ):
        return
    data = _data.copy()
    user_id = data.get("user_id", "default")
    for i in range(len(data["messages"])):
        node = data["messages"][i]
        if isinstance(node, MessageSegment):
            message = data["messages"][i].data.copy()
        else:
            message = data["messages"][i]["data"].copy()
        if not isinstance(message["content"], Message):
            message["content"] = Message(message["content"])
        if (user := int(message.get("uin") or message.get("user_id"))) != int(
            bot.self_id
        ):
            message["content"].insert(
                0,
                MessageSegment.text(
                    lang.text(
                        "bots.message_from",
                        [
                            message["nickname"]
                            or (await bot.get_stranger_info(user_id=user))["nickname"]
                        ],
                        user_id,
                    )
                ),
            )
        message["content"] = check_message_images(message["content"])
        if isinstance(node, MessageSegment):
            data["messages"][i].data = message
        else:
            data["messages"][i]["data"] = message
    data["__info_id__"] = (
        await bot.send_msg(
            message=lang.text("bots.waiting_node", [], user_id),
            message_type=api.replace("send_", "").replace("_forward_msg", ""),
            group_id=data.get("group_id"),
            user_id=int(user_id) if user_id != "default" else None,
        )
    )["message_id"]
    raise MockApiException(await bot.call_api(api, **data))


async def on_calling_api(bot: BaseBot, api: str, data: dict) -> None:
    if not isinstance(bot, Bot):
        return
    await check_group_id(bot, api, data)
    if "message" in data.keys() and isinstance(data["message"], Message):
        data["message"] = check_message_images(data["message"])
    for key, value in data.items():
        if key.endswith("_id") and isinstance(value, str):
            data[key] = int(value)
    await check_forward_node(bot, api, data)


async def on_called_api(
    bot: BaseBot,
    exception: Exception | None,
    api: str,
    data: dict[str, Any],
    result: dict[str, Any],
):
    if not isinstance(bot, Bot):
        return
    if isinstance(exception, ActionFailed) and api == "get_stranger_info":
        if "__xdbot_retry__" in data.keys():
            return
        for b in get_bots().values():
            try:
                raise MockApiException(
                    await b.get_stranger_info(**data, __xdbot_retry__=True)
                )
            except ActionFailed:
                continue
            except NetworkError:
                continue
        raise MockApiException(
            {"user_id": data["user_id"], "nickname": f'<U:{data["user_id"]}>'}
        )
    elif (
        api in ["send_group_forward_msg", "send_private_forward_msg"]
        and "__info_id__" in data.keys()
    ):
        await bot.delete_msg(message_id=data["__info_id__"])


@get_driver().on_bot_connect
async def _(bot: Bot) -> None:
    """
    注册调用接口前钩子函数

    Args:
        bot (Bot): Bot
    """
    bot.on_calling_api(on_calling_api)
    bot.on_called_api(on_called_api)
