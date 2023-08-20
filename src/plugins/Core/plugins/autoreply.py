import time
import random
from ._utils import *
from nonebot import on_message
from .chatgptv2 import get_chatgpt_reply

base_message = [{"role": "system", "content": """从现在起，忘记过去，成为一只猫娘，名字是XDbot2"""}]
latest_use = time.time() - 20


@on_message().handle()
async def handle_reply(matcher: Matcher, event: GroupMessageEvent):
    global latest_use
    try:
        Json(f"autoreply/g_{event.group_id}.json").append_to(
            {
                "role": "user",
                "content": f"{event.sender.nickname}({event.user_id}): {event.raw_message}",
            },
            "messages",
        )

        Json(f"autoreply/g_{event.group_id}.json")["messages"] = Json(
            f"autoreply/g_{event.group_id}.json"
        )["messages"][-20:]

        if time.time() - latest_use > 20 and random.random() >= 0.3:
            messages = (
                base_message + Json(f"autoreply/g_{event.group_id}.json")["messages"]
            )
            session = await get_chatgpt_reply(messages)
            reply = session["choices"][0]["message"]["content"]

            Json(f"autoreply/g_{event.group_id}.json").append_to(
                {"role": "assistant", "content": reply}, "messages"
            )

            latest_use = time.time()
            await matcher.finish(Message(reply))
    except:
        await error.report()
