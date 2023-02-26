import json


def send_message(text: str, receive: str,
                 sender_nickname: str = "System", sender_id: int = 3457603681):
    data = json.load(open("data/messenger.messageList.json"))
    data.append({
        "recv": receive,
        "text": text,
        "sender": {
            "nickname": sender_nickname,
            "user_id": sender_id
        }
    })
    json.dump(
        data,
        open(
            "data/messenger.messageList.json",
            mode="w",
            encoding="utf-8"))
