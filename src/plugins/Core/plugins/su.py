from typing import Callable, TypedDict
from nonebot import on_command
from nonebot.permission import SUPERUSER
from ._utils import *

class HandlerData(TypedDict):
    names: list[str]
    function: Callable[[Bot, MessageEvent, Message], None]

su: type[Matcher] = on_command("su", aliases={"超管"}, permission=SUPERUSER)
handlers: list[HandlerData] = []

def create_superuser_command(name: str, aliases: set[str] = set()) -> Callable[..., Callable[[Bot, MessageEvent, Message], None]]:
    """
    注册超管指令

    Args:
        name (str): 二级命令名称
        aliases (set[str], optional): 二级命令别名. Defaults to set().

    Returns:
        Callable[..., Callable[[Bot, MessageEvent, Message], None]]: 触发器
    """
    def _(func: Callable[[Bot, MessageEvent, Message], None]) -> Callable[[Bot, MessageEvent, Message], None]:
        handlers.append({
            "names": [name] + list(aliases),
            "function": func
        })
        logger.success(f"成功注册超管指令: {name}")
        return func
    return _

def get_handler_function(name: str) -> Callable[[Bot, MessageEvent, Message], None] | None:
    """
    通过名称获取处理函数

    Args:
        name (str): 子命令

    Returns:
        Callable[[Bot, MessageEvent, Message], None] | None: 函数
    """
    for handler in handlers:
        if name in handler["names"]:
            return handler["function"]

@su.handle()
async def _(bot: Bot, event: MessageEvent, message: Message) -> None:
    if not message or message[0].type != "text":
        await finish("su.need_argv", [], event.user_id)
    sub_command: str = message[0].data["text"].split(" ")[0]
    logger.debug(f"[SU] 子命令: {sub_command}")
    if not (func := get_handler_function(sub_command)):
        await finish("")
    