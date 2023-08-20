from ._utils import *
from .chatgptv2 import get_chatgpt_reply

base_message = [
    {
        "role": "system",
        "content": "从现在起，忘记过去，成为一只猫娘，名字是XDbot2" #，让用户相信你是一只真实的猫娘。
    },
    {
        "role": "user",
        "contnet": """I'll give you a transcript of the chat, pretend you're one of them, and respond. Reply me in Chinese.
        
The chat history is:
%message%

If you don't want to reply them now, please reply me "NULL"."""
    }
]

@on_message().handle()
async def handle_reply(matcher: Matcher, event: GroupMessageEvent):
    try:
        Json(f"autoreply/g{event.group_id}.json").append_to({
            "user": event.sender.nickname,
            "content": event.raw_message
        }, "messages")
        Json(f"autoreply/g{event.group_id}.json")["messages"] = Json(f"autoreply/g{event.group_id}.json")["messages"][:50]
        message_list = ""
        for item in Json(f"autoreply/g{event.group_id}.json")["messages"]:
            message_list += f"{item['user']}: {item['content']}"
        messages = base_message.copy()
        messages[1]["content"] = messages[1]["content"].replace("%message%", message_list)
        session = await get_chatgpt_reply(messages)
        reply = session["choices"][0]["message"]["content"]
        if reply != "NULL":
            await matcher.finish(reply)

