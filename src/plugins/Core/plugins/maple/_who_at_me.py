import os
import re
from typing import cast, List, Dict, Tuple

from nonebot import on_command, on_regex, on_message
from nonebot.adapters.onebot.v11 import GroupMessageEvent

from ._rule import group
from ._store import JsonDict
from ._onebot import (
    MessageID,
    MessageType,
    send_group_forward_msg,
    custom_forward_node,
    get_group_msg_history,
    get_user_name
)


MessageNode = Dict[str, str | int]

AT_PATTERN = r"\[CQ:at,qq=(\d+|all)\]"

PREVIOUS_MESSAGE_COUNT = 7
NEXT_MESSAGE_COUNT = 7
assert PREVIOUS_MESSAGE_COUNT <= 18


def message_to_node(message: MessageType) -> Tuple[MessageID, MessageNode]:
    return cast(MessageID, message["message_id"]), {
        "time": cast(int, message["time"]),
        "user_id": cast(str, message["user_id"]),
        "content": cast(str, message["raw_message"])
    }


@on_regex(AT_PATTERN).handle()
async def at_handle(event: GroupMessageEvent) -> None:
    history = JsonDict(os.path.join("wam", f"{event.group_id}.json"), dict)
    messages = await get_group_msg_history(event.group_id)
    messages = messages[-(1 + PREVIOUS_MESSAGE_COUNT):-1]
    messages = list(map(message_to_node, messages))
    message_ids: List[MessageID] = []
    for message_id, node in messages:
        message_ids.append(message_id)
        cast(Dict[str, MessageNode], history["nodes"])[str(message_id)] = node
    message_ids.append(event.message_id)
    cast(Dict[str, MessageNode], history["nodes"])[str(event.message_id)] = {
        "time": event.time,
        "user_id": event.user_id,
        "content": event.raw_message
    }
    target_ids = set(re.findall(AT_PATTERN, cast(str, event.raw_message)))
    if "all" in target_ids:
        target_ids = {"all"}
    for target_id in target_ids:
        cast(Dict[str, List[MessageID]], history[target_id])[
            str(event.message_id)] = message_ids
    history.save()

    message_count = NEXT_MESSAGE_COUNT
    matcher = on_message(group(event.group_id))

    @matcher.handle()
    async def at_successor_handle(sub_event: GroupMessageEvent) -> None:
        node: MessageNode = {
            "time": sub_event.time,
            "user_id": sub_event.user_id,
            "content": sub_event.raw_message
        }
        history = JsonDict(os.path.join("wam", f"{event.group_id}.json"), dict)
        cast(Dict[str, MessageNode], history["nodes"])[
            str(sub_event.message_id)] = node
        for target_id in target_ids:
            cast(Dict[str, List[MessageID]], history[target_id])[
                str(event.message_id)].append(sub_event.message_id)
        history.save()
        nonlocal message_count
        message_count -= 1
        if message_count == 0:
            matcher.destroy()


@on_command("who-at-me", aliases={"wam"}).handle()
async def who_at_me_handle(event: GroupMessageEvent) -> None:
    def get_node(message_id: MessageID) -> MessageNode:
        return cast(Dict[str, MessageNode], history["nodes"])[str(message_id)]

    history = JsonDict(os.path.join("wam", f"{event.group_id}.json"), dict)
    messages = cast(List[List[MessageID]], list(
        history[str(event.user_id)].values()))
    messages += list(filter(
        lambda node:
            get_node(node[PREVIOUS_MESSAGE_COUNT])["user_id"] != event.user_id,
        cast(List[List[MessageID]], history["all"].values())))
    messages.sort(key=lambda node: get_node(
        node[PREVIOUS_MESSAGE_COUNT])["time"], reverse=True)

    async def subs(content: str) -> str:
        for matched in re.findall(AT_PATTERN, content):
            content = content.replace(f"[CQ:at,qq={matched}]", "[[@{}]]".format(
                "全体成员" if matched == "all"
                else await get_user_name(matched, event.group_id)
            ))
        return content

    await send_group_forward_msg(event.group_id, [
        await custom_forward_node(
            time=(node := get_node(
                message_ids[PREVIOUS_MESSAGE_COUNT]))["time"],
            user_id=node["user_id"],
            group_id=event.group_id,
            content=[
                await custom_forward_node(
                    time=(node := get_node(message_id))["time"],
                    user_id=node["user_id"],
                    group_id=event.group_id,
                    content=await subs(cast(str, node["content"]))
                )
                for message_id in message_ids
            ]
        )
        for message_ids in messages
    ])
