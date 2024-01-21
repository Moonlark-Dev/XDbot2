import json
import os
import os.path
from typing import Any, Callable, Union
import httpx

# 快捷访问
from nonebot import on_message
from nonebot import on_command
from nonebot.log import logger
from nonebot.permission import SUPERUSER
from nonebot.params import CommandArg
from nonebot.matcher import Matcher
from . import _error as error
from . import _lang as lang
from nonebot.adapters.onebot.v11 import GroupMessageEvent
from nonebot.adapters.onebot.v11 import MessageEvent
from nonebot.adapters.onebot.v11.bot import Bot
from nonebot.adapters.onebot.v11 import Message
from nonebot.adapters.onebot.v11 import MessageSegment

# import traceback

SUCCESS: bool = True
FAILED: bool = False
SKIP: None = None


def create_command(cmd: str, aliases: set = set(), **kwargs):
    matcher = on_command(cmd, aliases=aliases, **kwargs)

    def deco(func: Callable):
        async def handler(
            bot: Bot, event: MessageEvent, message: Message = CommandArg()
        ):
            try:
                logger.info(f"处理模块: {func.__module__}")
                await func(bot, event, message)
            except:
                await error.report()

        matcher.append_handler(handler)
        return handler

    return deco


def create_group_command(cmd: str, aliases: set = set(), **kwargs):
    matcher = on_command(cmd, aliases=aliases, **kwargs)

    def deco(func):
        async def handler(
            bot: Bot, event: MessageEvent, message: Message = CommandArg()
        ):
            if not isinstance(event, GroupMessageEvent):
                await finish(get_currency_key("need_group"), [], event.user_id)
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
    parse_cq_code: bool = False,
) -> None:
    await matcher.finish(
        Message(lang.text(key, _format, user_id))
        if parse_cq_code
        else lang.text(key, _format, user_id),
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

    def update(self, obj: dict):
        self.data.update(obj)
        for key in list(obj.keys()):
            self.changed_key.add(key)
        self.save()

    def to_dict(self) -> dict:
        return self.data.copy()

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
            if not self.changed_key.__len__():
                return
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

    def add(self, key: str, i: int) -> int:
        if not isinstance(self.get(key, 0), int):
            self[key] = 0
        self[key] += 1
        self.changed_key.add(key)
        self.save()
        return self[key]

    def items(self):
        return list(self.data.items())

    def keys(self):
        return list(self.data.keys())


async def generate_node_message(bot: Bot, messages: list[str | Message]) -> Message:
    message = Message()
    nickname = (await bot.get_login_info())["nickname"]
    for content in messages:
        message.append(MessageSegment.node_custom(int(bot.self_id), nickname, content))
    return message


async def send_node_message(bot: Bot, messages: Message, event: MessageEvent) -> None:
    await bot.call_api(
        f"send_{'group' if event.get_session_id().startswith('group') else 'private'}_forward_msg",
        messages=messages,
        user_id=event.user_id,
        group_id=event.dict().get("group_id"),
    )


def get_currency_key(key: str) -> str:
    # 写这个函数纯粹是因为记不住 get_currency_key 这个词
    return f"currency.{key}"


async def get_group_id(event: MessageEvent) -> int:
    if (group_id := event.dict().get("group_id")) is None:
        await finish(get_currency_key("need_group"), [], event.user_id)
    return int(group_id)


async def context_review(
    context: str, _type: str, user_id: Union[int, str] = "未知"
) -> dict:
    # 目前可用 type: url, text
    # type 为 url 时 context 需以 http:// 或 https:// 开头, url 内容是一张图片
    async with httpx.AsyncClient() as client:
        response = await client.post(f"http://localhost:5000/{_type}",json={"context":context})
    result = response.json()
    if result["conclusionType"] == 2:  # 不合规
        await error.report(
            f"「内容违规提醒」\n来自用户: {user_id}\n类型: {_type}\nLog ID: {result['log_id']}"
        )
    return result
