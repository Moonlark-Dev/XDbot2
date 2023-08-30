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
from nonebot.adapters.onebot.v11.bot import Bot
from nonebot.adapters.onebot.v11 import Message

# import traceback

SUCCESS: bool = True
FAILED: bool = False


def create_command(cmd: str, aliases: set = set(), **kwargs):
    matcher = on_command(cmd, aliases=aliases, **kwargs)
    def deco(func):
        async def handler(bot: Bot, event: MessageEvent, message: Message = CommandArg()):
            try:
                await func(bot, event, message)
            except:
                await error.report()
        matcher.append_handler(handler)
        return handler
    return deco


async def send_text(
    key: str,
    _format: list = [],
    user_id: str | int = "default",
    at_sender: bool = False,
    reply_message: bool = False,
    matcher: Matcher = Matcher(),
) -> None:
    await matcher.send(
        Message(lang.text(key, _format, user_id)),
        at_sender=at_sender,
        reply_message=reply_message,
    )


async def finish(
    key: str,
    _format: list = [],
    user_id: str | int = "default",
    at_sender: bool = True,
    reply_message: bool = False,
    matcher: Matcher = Matcher(),
) -> None:
    await matcher.finish(
        lang.text(key, _format, user_id),
        at_sender=at_sender,
        reply_message=reply_message,
    )


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
