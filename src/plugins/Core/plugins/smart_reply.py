import random
from nonebot.params import ArgPlainText
from nonebot.typing import T_State
import re
import difflib
import os.path
from nonebot import on_message
from ._utils import *
from .su import su
from .etm import economy


def get_rules(group_id: int):
    try:
        return os.listdir(f"data/reply/g{group_id}/")
    except OSError:
        return []


def is_matched_rule(rule_id: str, group_id: int, message: str):
    try:
        data = Json(f"reply/g{group_id}/{rule_id}.json")["match"]
        match data["type"]:
            case "regex":
                return bool(re.match(re.compile(data["text"], re.DOTALL), message))
            case "keyword":
                return data["text"] in message
            case "fullmatch":
                return data["text"] == message
            case "fuzzymatch":
                return (
                    difflib.SequenceMatcher(None, data["text"], message).ratio() >= 0.75
                )
    except:
        pass


def get_rule_reply(rule_id: str, group_id: int):
    return random.choice(Json(f"reply/g{group_id}/{rule_id}.json")["reply"])


@on_message().handle()
async def match_rules(matcher: Matcher, event: GroupMessageEvent):
    message = str(event.get_message())
    for _rule_id in get_rules(event.group_id):
        rule_id = _rule_id.replace(".json", "")
        if is_matched_rule(rule_id, event.group_id, message):
            await matcher.finish(get_rule_reply(rule_id, group_id))


def get_matcher_type(argv: str):
    reply_matcher_types = [
        ["regex", "re", "正则", "正则表达式"],
        ["keyword", "kwd", "关键词"],
        ["fullmatch", "full", "完全匹配"],
        ["fuzzymatch", "fuzzy", "模糊匹配"],
    ]
    for _type in reply_matcher_types:
        if argv in _type:
            return _type[0]


def get_reply_id(group_id: int):
    length = 0
    while True:
        if not os.path.isfile(f"data/reply/g{group_id}/{length}.json"):
            return length
        else:
            length += 1


def create_matcher(
    user_id: str,
    group_id: int,
    matcher_type: str,
    matcher_data: str,
    reply_text: list[str],
):
    reply_id = get_reply_id(group_id)
    Json(f"reply/g{group_id}/{reply_id}.json").set_to(
        {
            "id": reply_id,
            "match": {"type": matcher_type, "text": matcher_data},
            "reply": reply_text,
            "group_id": group_id,
            "user_id": user_id,
        }
    )
    return reply_id


reply_command = on_command("reply", aliases={"调教"})


@reply_command.handle()
async def handle_reply(
    state: T_State,
    matcher: Matcher,
    event: GroupMessageEvent,
    message: Message = CommandArg(),
):
    try:
        argv = message.extract_plain_text().splitlines()[0].split(" ")

        if argv[0] in ["add", "添加"]:
            state["matcher_type"] = get_matcher_type(argv[1])
            if len(message.extract_plain_text().splitlines()) > 1:
                matcher.set_arg(
                    "match_text",
                    Message("\n".join(message.extract_plain_text().splitlines()[1:])),
                )
                # await send_text("reply.add_reply_text", [], event.user_id)
            else:
                await send_text("reply.add_match_text", [], event.user_id)

    except:
        await error.report()


@reply_command.got("match_text")
async def receive_matchtext(
    state: T_State, event: GroupMessageEvent, match_text: str = ArgPlainText()
):
    try:
        if match_text in ["cancel", "取消"]:
            await finish("reply.canceled", [], event.user_id)
        state["match_text"] = match_text
        state["_reply_text"] = []
        await send_text("reply.add_reply_text", [], event.user_id)
    except:
        await error.report()


@reply_command.got("reply_text")
async def receive_replytext(
    state: T_State, event: GroupMessageEvent, reply_text: str = ArgPlainText()
):
    if reply_text in ["cancel", "取消"]:
        await finish("reply.canceled", [], event.user_id)
    if reply_text in ["finish", "ok", "完成"]:
        await finish(
            "reply.done",
            [
                create_matcher(
                    event.get_user_id(),
                    event.group_id,
                    state["matcher_type"],
                    state["match_text"],
                    state["_reply_text"],
                )
            ],
            event.user_id,
        )
    state["_reply_text"].append(reply_text)
    await reply_command.reject(lang.text("reply.reject", [], event.user_id))
