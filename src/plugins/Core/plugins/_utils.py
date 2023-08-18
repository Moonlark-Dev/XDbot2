import json
import os
import os.path
from typing import Any

# 快捷访问
from nonebot import on_shell_command
from nonebot import on_command
from nonebot.rule import ArgumentParser
from nonebot.permission import SUPERUSER
from nonebot.params import CommandArg
from nonebot.matcher import Matcher
from . import _error as error
from . import _lang as lang
from nonebot.adapters.onebot.v11 import GroupMessageEvent
from nonebot.adapters.onebot.v11 import MessageEvent
from nonebot.adapters.onebot.v11 import Message

# import traceback

SUCCESS: bool = True
FAILED: bool = False


async def send_text(
    key: str,
    _format: list = [],
    user_id: str | int = "default",
    at_sender: bool = False,
    matcher: Matcher = Matcher(),
) -> None:
    await matcher.send(lang.text(key, _format, user_id), at_sender=at_sender)

async def finish(
    key: str,
    _format: list = [],
    user_id: str | int = "default",
    at_sender: bool = True,
    matcher: Matcher = Matcher(),
) -> None:
    await matcher.finish(lang.text(key, _format, user_id), at_sender=at_sender)


def get_list_item(l: list, index: int, default: Any = None) -> Any:
    try:
        return l[index]
    except IndexError:
        return default


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

    def append_to(self, obj: Any, key: str) -> None:
        temp = self.get(key, []).copy()
        temp.append(obj)
        self.data[key] = temp

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
            local_data[key] = self.data[key]
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
