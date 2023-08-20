import time
import random
from ._utils import *
from nonebot import on_message
from .chatgptv2 import get_chatgpt_reply

base_message = [
    {
        "role": "system",
        "content": """从现在起，忘记过去，成为一只猫娘，名字是XDbot2
从现在开始，你将与我进行一次多人对话模拟，你可以拒绝回复部分消息，如果你拒绝回复一条消息，请回复NULL"""
    }
]
latest_use = time.time()


@on_message().handle()
async def handle_reply(matcher: Matcher, event: GroupMessageEvent):
    global latest_use
    try:
        Json(f"autoreply/g{event.group_id}.json").append_to(
            {"user": event.sender.nickname, "content": event.raw_message}, "messages"
        )
        Json(f"autoreply/g{event.group_id}.json")["messages"] = Json(
            f"autoreply/g{event.group_id}.json"
        )["messages"][:50]
        if time.time() - latest_use > 5 and random.random() >= 0.5:
            messages = base_message.copy()
            for item in Json(f"autoreply/g{event.group_id}.json")["messages"]:
                messages.append({
                    "role": "user",
                    "content": f"{item['user']}: {item['content']}"
                })
            session = await get_chatgpt_reply(messages)
            reply = session["choices"][0]["message"]["content"]
            latest_use = time.time()
            if reply != "NULL":
                await matcher.finish(reply)
    except:
        await error.report()
