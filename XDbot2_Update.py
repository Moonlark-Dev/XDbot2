# XDbot2 develop 2308302007

# /!\ 提示：
# 此文件为 XDbot2 更新脚本，用于更改部分数据以便 XDbot2 正常运行
# 文件第一行为版本标识符，供 XDbot2 Updater 识别版本

import json
from typing import Any
import os
import os.path

class Json:
    def __init__(self, path: str) -> None:
        self.path = os.path.join("data", path)
        self.changed_key = set()

        try:
            os.makedirs(os.path.dirname(self.path))
        except:
            pass

        if not os.path.isfile(self.path):
            self.data = {}
        else:
            self.data = json.load(open(file=self.path, encoding="utf-8"))

    def set_to(self, obj: dict):
        self.data.update(obj)
        for key in list(obj.keys()):
            self.changed_key.add(key)
        self.save()

    def to_dict(self) -> dict:
        return self.data

    def append_to(self, obj: Any, key: str) -> None:
        self.data[key] = self.get(key, []) + [obj]
        self.changed_key.add(key)
        self.save()

    def __setitem__(self, key: str, value: Any) -> None:
        if value == None:
            self.data.pop(str(key))
        else:
            self.data[str(key)] = value
        self.changed_key.add(key)
        self.save()  # 保存

    def pop(self, key: str) -> Any:
        try:
            return self.data.pop(key)
        except:
            return None

    # def __getattr__(self, item: str) -> any:
    # return self.get(item)

    def __getitem__(self, key: str) -> Any:
        return self.get(key)

    def __del__(self) -> None:
        self.save()

    def save(self) -> None:
        try:
            local_data = json.load(open(file=self.path, encoding="utf-8"))
        except FileNotFoundError:
            local_data = {}
        for key in list(self.changed_key):
            try:
                local_data[key] = self.data[key]
            except KeyError:
                local_data.pop(key)
        json.dump(local_data, open(self.path, "w", encoding="utf-8"))
        self.changed_key = set()

    def get(self, key: str, default: Any = None) -> Any:
        try:
            return self.data[key]
        except:
            if default is None:
                return None
            self.data[key] = default
            self.changed_key.add(key)
            return self.get(key, default)

    def items(self):
        return list(self.data.items())


def get_reply_id(group_id: int):
    length = 0
    while True:
        if not os.path.isfile(f"data/reply/g{group_id}/{length}.json"):
            return length
        else:
            length += 1

async def create_matcher(
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


def get_list() -> dict:
    data = json.load(open("data/smart_reply.data.json", encoding="utf-8"))
    data.pop("count")
    return data.copy()

for data in list(get_list().values()):
    create_matcher(
        data["user_id"],
        data["group_id"],
        "regex",
        data["matcher"],
        data["reply"]
    )