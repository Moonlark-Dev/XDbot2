import json
import os
import os.path
import traceback
from typing import Any, Awaitable, Callable, Optional, Type, Union
import httpx
from .etm.exception import *

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
from nonebot.typing import T_State
from nonebot.rule import Rule

# import traceback

SUCCESS: bool = True
FAILED: bool = False
SKIP: None = None

SIMPLE_HANDLER = Callable[[Bot, MessageEvent, Message], Awaitable[None]]
GROUP_HANDLER = Callable[[Bot, GroupMessageEvent, Message], Awaitable[None]]
HANDLER_WITH_STATE = Callable[[Bot, MessageEvent, Message, T_State], Awaitable[None]]


async def execute_function(
    func: Awaitable[Any], event: MessageEvent, cmd: Optional[str]
) -> None:
    try:
        await func
    except IndexError as e:
        if "arg" in traceback.format_exc():
            await finish(get_currency_key("wrong_argv"), [cmd], event.user_id)
    except IllegalQuantityException as e:
        await finish("_utils.IllegalQuantityException", [e.args[0]], event.user_id)
    except UserDataLocked as e:
        await finish("_utils.UserDataLocked", [], event.user_id)
    except NoPawCoinException:
        await finish("_utils.noPawCoin", [], event.user_id)
    except Exception:
        await error.report()
        # pass


def create_message_handler_with_state(rule: Optional[Rule] = None):
    matcher = on_message(rule)

    def deco(func: HANDLER_WITH_STATE):
        async def handler(bot: Bot, event: MessageEvent, state: T_State) -> None:
            await execute_function(
                func(bot, event, event.get_message(), state), event, None
            )

        matcher.append_handler(handler)
        return handler

    return deco


def create_message_handler(rule: Optional[Rule] = None):
    matcher = on_message(rule)

    def deco(func: SIMPLE_HANDLER):
        async def handler(bot: Bot, event: MessageEvent) -> None:
            await execute_function(func(bot, event, event.get_message()), event, None)

        matcher.append_handler(handler)
        return handler

    return deco


class UnsupportPublicQQBot(Exception):
    pass


def check_qqbot(bot_id: str) -> None:
    if bot_id in Json("qqbots.json")["bots"]:
        raise UnsupportPublicQQBot


def create_command(cmd: str, aliases: set = set(), **kwargs):
    matcher = on_command(cmd, aliases=aliases, **kwargs)

    def deco(func: SIMPLE_HANDLER):
        async def handler(
            bot: Bot, event: MessageEvent, message: Message = CommandArg()
        ):
            await execute_function(func(bot, event, message), event, cmd)

        matcher.append_handler(handler)
        return handler

    return deco


def create_group_command(cmd: str, aliases: set = set(), **kwargs):
    matcher = on_command(cmd, aliases=aliases, **kwargs)

    def deco(func: GROUP_HANDLER):
        async def handler(
            bot: Bot, event: MessageEvent, message: Message = CommandArg()
        ):
            if not isinstance(event, GroupMessageEvent):
                await finish(get_currency_key("need_group"), [], event.user_id)
            await execute_function(func(bot, event, message), event, cmd)

        matcher.append_handler(handler)
        return handler

    return deco


async def send_message(
    bot: Bot, event: MessageEvent, key: str, _format: list = []
) -> int:
    return (
        await bot.send_msg(
            message_type=event.message_type,
            user_id=event.user_id,
            group_id=event.dict().get("group_id"),
            message=Message(lang.text(key, _format, event.user_id)),
        )
    )["message_id"]


def get_prefix_list() -> list[str]:
    return Json("init.json")["config"]["command_start"]


async def send_text(
    key: str,
    _format: list = [],
    user_id: str | int = "default",
    at_sender: bool = False,
    reply_message: bool = False,
    matcher: Matcher = Matcher(),
) -> None:
    await matcher.send(
        message=Message(lang.text(key, _format, user_id)),
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
    **kwargs,
) -> None:
    await matcher.finish(
        (
            Message(lang.text(key, _format, user_id, params=kwargs))
            if parse_cq_code
            else lang.text(key, _format, user_id)
        ),
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
        json.dump(local_data, open(self.path, "w", encoding="utf-8"), indent=4)
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
        response = await client.post(
            f"http://localhost:5000/{_type}", json={"context": context}
        )
    result = response.json()
    try:
        if result["conclusionType"] == 2:  # 不合规
            reasons = [i["msg"] for i in result["data"]]
            await error.report(
                f"「内容违规提醒」\n来自用户: {user_id}\n类型: {_type}\nLog ID: {result['log_id']}\n违规原因:\n"
                + "\n".join(reasons)
            )
    except KeyError:
        await error.report(
            f"「审核失败提醒」\n来自用户: {user_id}\n类型: {_type}\nLog ID: {result['log_id']}\nError Code: {result['error_code']}\nError Msg: {result['error_msg']}"
        )
        return {
            "log_id": result["log_id"],
            "conclusion": "不合规",
            "conclusionType": 2,
            "data": [
                {
                    "type": 0,
                    "subType": 0,
                    "conclusion": "不合规",
                    "conclusionType": 2,
                    "msg": "审核失败默认不通过",
                }
            ],
        }
    return result


def get_bool(string: str, default: bool) -> Optional[bool]:
    match string.lower():
        case "on" | "开启" | "true" | "enable" | "启用":
            return True
        case "off" | "关闭" | "false" | "disable" | "禁用":
            return False
        case _:
            return not default


async def set_switch(file: str, key: str, input_: str, user_id: str | int) -> None:
    Json(file)[key] = get_bool(input_, Json(file)[key])
    await finish("_utils.switch", [key, Json(file)[key]], user_id)
