import json
from . import _messenger as messenger
from . import _error

def get_list() -> dict:
    data =  json.load(open("data/smart_reply.data.json"))
    data.pop("count")
    return data.copy()

async def create_reply(matcher: str, strings: list[str], group_id: int, user_id: str) -> int:
    data = json.load(open("data/smart_reply.data.json"))
    data[str(data["count"])] = {
        "matcher": matcher,
        "text": strings,
        "global": False,
        "group_id": group_id,
        "user_id": user_id
    }
    await _error.report((
        f"「新调教投稿（#{data['count']}）」\n"
        f"表达式：{matcher}\n"
        f"文本：{'\n'.join(strings)}"
        f"group_{group_id}_{user_id}"
    ))
    await _error.report((
        f"使用 /su reply global {data['count']} 设为全局\n"
        f"使用 /su reply remove {data['count']} 删除"
    ))
    data["count"] += 1
    json.dump(data, open("data/smart_reply.data.json", "w"))
    return data["count"] - 1

def remove_reply(reply_id: str, user_id: str, force: bool = False) -> bool:
    data = json.load(open("data/smart_reply.data.json"))
    if data["user_id"] == user_id or force:
        data.pop(reply_id)
        json.dump(data, open("data/smart_reply.data.json", "w"))
        return True
    else:
        return False

def global_reply(reply_id: str) -> None:
    data = json.load(open("data/smart_reply.data.json"))
    data[reply_id]["global"] = True
    json.dump(data, open("data/smart_reply.data.json", "w"))

    messenger.send_message(f"您提交的 Reply#{reply_id} 已被全局化", data[reply_id]["user_id"])
    

