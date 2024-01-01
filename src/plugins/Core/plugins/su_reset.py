import asyncio
from .etm import data, bag
from .send_email import send_email
import random
from typing import Optional
from ._utils import *
from .su import create_superuser_command

reset_cache: dict[str, int | None] = {}


def get_user_id(message: MessageSegment) -> Optional[int]:
    """
    获取消息段中的用户ID

    Args:
        message (MessageSegment): 消息段

    Returns:
        Optional[int]: 用户ID
    """
    match message.type:
        case "at":
            user_id: Any | None = message.data.get("user_id") or message.data.get("qq")
        case "text":
            user_id: Any | None = message.data["text"]
        case _:
            return
    try:
        return int(user_id)  # type: ignore
    except ValueError:
        return


def get_cache_id() -> str:
    """
    获取缓存ID

    Returns:
        str: ID
    """
    cache_id: str = "".join(random.choices("1234567890abcdefghijklmnopqrstuvwxyz", k=6))
    if cache_id in reset_cache.keys():
        return get_cache_id()
    return cache_id


@create_superuser_command("reset", {"重置", "重置账户"})
async def _(bot: Bot, event: MessageEvent, message: Message) -> None:
    if not message:
        await finish("su.need_argv", [], event.user_id)
    if not (user_id := get_user_id(message[0])):
        await finish("su.unknown_user", [message[0]], event.user_id)
    cache_id: str = get_cache_id()
    reset_cache[cache_id] = user_id
    await send_text("su.reset_confirm", [user_id, cache_id], event.user_id)
    await asyncio.sleep(180)
    if reset_cache.pop(cache_id) is not None:
        await finish("su.reset_timeout", [], event.user_id)


@create_superuser_command("reset-confirm", {"重置确认"})
async def _(bot: Bot, event: MessageEvent, message: Message) -> None:
    cache_id = message.extract_plain_text()
    if not reset_cache.get(cache_id):
        await finish("su.unknown_argv", [cache_id], event.user_id)
    user_id: str = str(reset_cache[cache_id])
    bag.bags.pop(user_id, None)
    data.achi_unlock_progress.pop(user_id, None)
    data.achi_user_data.pop(user_id, None)
    data.bags.pop(user_id, None)
    data.bank_lead_data.pop(user_id, None)
    data.buff.pop(user_id, None)
    data.emails.pop(user_id, None)
    data.basic_data.pop(user_id, None)
    await send_email(
        str(user_id),
        lang.text("su.reset_email_subject_nb", [], user_id),
        lang.text("email.no_data", [], user_id),
    )
    reset_cache[cache_id] = None
    await finish("currency.ok", [], event.user_id)
