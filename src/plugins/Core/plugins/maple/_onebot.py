from typing import List, Dict, Optional

from nonebot import get_bot
from nonebot.adapters import Message, MessageSegment, MessageTemplate
from typing import cast


UserID = GroupID = MessageID = str | int
AnyMessage = str | Message | MessageSegment | MessageTemplate
MessageType = Dict[str, int | str | Dict[str, int | str]]
ForwardNode = Dict[str, str | Dict[str, str |
                                   int | AnyMessage | List["ForwardNode"]]]


async def send_group_msg(group_id: GroupID, message: AnyMessage) -> MessageID:
    return (await get_bot().send_group_msg(
        group_id=int(group_id),
        message=message
    ))["message_id"]


async def delete_msg(message_id: MessageID) -> None:
    await get_bot().delete_msg(message_id=int(message_id))


async def get_group_member_info(
    group_id: GroupID,
    user_id: UserID,
    no_cache: bool = False
) -> Dict[str, str]:
    return await get_bot().get_group_member_info(
        group_id=int(group_id),
        user_id=int(user_id),
        no_cache=no_cache
    )


async def get_stranger_info(
    user_id: UserID,
    no_cache: bool = False
) -> Dict[str, str]:
    return await get_bot().get_stranger_info(
        user_id=int(user_id),
        no_cache=no_cache
    )


async def custom_forward_node(
    user_id: UserID,
    content: AnyMessage | List[ForwardNode],
    name: Optional[str] = None,
    group_id: Optional[GroupID] = None,
    time: Optional[int | str] = None
) -> ForwardNode:
    if name is None:
        name = await get_user_name(user_id, group_id)
    node: ForwardNode = {
        "type": "node",
        "data": {
            "name": name,
            "uin": str(user_id),
            "content": content
        }
    }
    if time is not None:
        cast(Dict[str, int | str], node["data"])["time"] = int(time)
    return node


def referencing_forward_node(id: MessageID) -> ForwardNode:
    return {
        "type": "node",
        "data": {
            "id": str(id)
        }
    }


async def send_group_forward_msg(
    group_id: GroupID,
    messages: List[ForwardNode],
) -> None:
    await get_bot().send_group_forward_msg(
        group_id=int(group_id),
        messages=messages
    )


async def get_group_msg_history(
    group_id: GroupID,
    message_seq: Optional[MessageID] = None
) -> List[MessageType]:
    return (await get_bot().get_group_msg_history(
        message_seq=message_seq,
        group_id=int(group_id)
    ))["messages"]


async def get_user_name(
    user_id: UserID,
    group_id: Optional[GroupID] = None
) -> str:
    if group_id is None:
        return (await get_stranger_info(user_id=int(user_id)))["nickname"]
    else:
        info = await get_group_member_info(group_id, user_id)
        return info["card"] or info["nickname"]
