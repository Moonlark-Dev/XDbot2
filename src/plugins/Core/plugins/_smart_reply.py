import json
from . import _messenger as messenger
from . import _error


def get_list() -> dict:
    data = json.load(open("data/smart_reply.data.json", encoding="utf-8"))
    data.pop("count")
    return data.copy()


async def create_reply(
    matcher: str, strings: list[str], group_id: int, user_id: str
) -> int:
    data = json.load(open("data/smart_reply.data.json", encoding="utf-8"))
    data[str(data["count"])] = {
        "matcher": matcher,
        "text": strings,
        "global": False,
        "group_id": group_id,
        "user_id": user_id,
    }
    await _error.report(
        (
            f"「新调教投稿（#{data['count']}）」\n"
            f"表达式：{matcher}\n"
            f"文本：{strings}\n"
            f"group_{group_id}_{user_id}"
        )
    )
    data["count"] += 1
    json.dump(data, open("data/smart_reply.data.json", "w", encoding="utf-8"))
    return data["count"] - 1


def remove_reply(reply_id: str, user_id: str, force: bool = False) -> bool:
    data = json.load(open("data/smart_reply.data.json"))
    if data[reply_id]["user_id"] == user_id or force:
        user_id = data.pop(reply_id)["user_id"]
        json.dump(data, open("data/smart_reply.data.json", "w", encoding="utf-8"))
        if force:
            messenger.send_message(f"您提交的 Reply#{reply_id} 已被超管删除！", user_id)
        return True
    else:
        return False


def global_reply(reply_id: str) -> None:
    data = json.load(open("data/smart_reply.data.json", encoding="utf-8"))
    data[reply_id]["global"] = True
    json.dump(data, open("data/smart_reply.data.json", "w", encoding="utf-8"))

    messenger.send_message(f"您提交的 Reply#{reply_id} 已被全局化", data[reply_id]["user_id"])
