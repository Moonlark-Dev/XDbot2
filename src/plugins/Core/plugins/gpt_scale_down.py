from ._utils import *
from .chatgptv2 import (
    get_session_messages,
    get_user_session,
    add_message_to_session,
    reset_session,
    get_chatgpt_reply,
)
from nonebot_plugin_apscheduler import scheduler


async def scale_session(session_id: str) -> str | None:
    add_message_to_session(session_id, "system", "请总结这个会话包含的要点")
    memory = (
        (await get_chatgpt_reply(get_session_messages(session_id)))
        .choices[0]
        .message.content
    )
    reset_session(session_id, "default")
    add_message_to_session(session_id, "user", memory or "")
    return memory


# [HELPSTART] Version: 2
# Command: gpt-scale
# Msg: 缩减GPT会话
# Info: 缩减当前 XDbot2GPT 会话（可能丢失部分信息）
# Usage: gpt-scale
# [HELPEND]


@create_command("gpt-scale")
async def _(
    bot: Bot, event: MessageEvent, message: Message, matcher: Matcher = Matcher()
) -> None:
    await matcher.finish(await scale_session(get_user_session(event.get_user_id())))


@scheduler.scheduled_job("cron", hour="0", minute="0", second="0", id="scale_sessions")
async def scale_sessions() -> None:
    for session_id in os.listdir("data/gpt/sessions"):
        if len(get_session_messages(session_id)) < 5:
            continue
        await scale_session(session_id)
