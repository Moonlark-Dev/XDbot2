import time
import traceback
from nonebot.log import logger
import pypinyin
from ._utils import *


async def get_messages(bot: Bot, group_id: int) -> list:
    """
    获取指定群聊十分钟内的历史消息

    Args:
        bot (Bot): OneBot V11 Bot对象
        group_id (int): 群号
        message_id (int): 开始消息ID

    Returns:
        list: 消息列表
    """
    messages = []
    message_seq = 0
    while True:
        try:
            if message_seq == 0:
                message_list = await bot.call_api(
                    "get_group_msg_history",
                    group_id=group_id
                )
            else:
                message_list = await bot.call_api(
                    "get_group_msg_history",
                    message_seq=message_seq,
                    group_id=group_id
                )
        except Exception:
            logger.warning(traceback.format_exc())
            break
        for message in message_list["messages"][::-1]:
            if time.time() - message["time"] <= 600:
                messages.append(message["raw_message"])
                message_seq = message["message_seq"]
            else:
                return messages
    return messages


def get_text_length(messages: list[str]) -> int:
    """
    获取消息记录中的总字数

    Args:
        messages (list[str]): 消息列表

    Returns:
        int: 总字数
    """
    length = 0
    for message in messages:
        length += len(message)
    return length


def get_ma_count(messages: list[str]) -> int:
    """
    获取「妈」在消息中出现的次数

    Args:
        messages (list[str]): 消息列表

    Returns:
        int: 「妈」出现的次数
    """
    count = 0
    for message in messages:
        for word in pypinyin.pinyin(message, style=pypinyin.Style.FIRST_LETTER):
            for pinyin in word:
                if "m" in pinyin:
                    count += 1
                    break
    return count


# [HELPSTART] Version: 2
# Command: ma-count
# Info: 计算近 10 分钟消息含妈量
# Msg: 计算含妈量
# Usage: ma-count
# [HELPEND]


@create_group_command("m-count", {"ma-count", "含妈量"})
async def handle_ma_count_command(bot: Bot, event: GroupMessageEvent, message: Message):
    await finish("macount.info", [
        round(
            (ma_count := get_ma_count(message_list := await get_messages(bot, event.group_id))) / (message_length := get_text_length(message_list)) * 100,
            3
        ),
        ma_count, message_length
    ], event.user_id, False, True)   
