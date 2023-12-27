from typing import Awaitable, Callable, Optional, TypeAlias, TypedDict
from ._utils import *

HANDLE_FUNC: TypeAlias = Callable[[Bot, MessageEvent, Message], Awaitable[None]]

class HandlerData(TypedDict):
    names: list[str]
    function: HANDLE_FUNC


su: type[Matcher] = on_command("su", aliases={"超管"}, permission=SUPERUSER)
handlers: list[HandlerData] = []


def create_superuser_command(name: str, aliases: set[str] = set()) -> Callable[..., HANDLE_FUNC]:
    """
    注册 su 指令

    Args:
        name (str): 指令名称
        aliases (set[str], optional): 别名. Defaults to set().

    Returns:
        Callable[..., HANDLE_FUNC]: 触发器
    """
    
    def _(func: HANDLE_FUNC) -> HANDLE_FUNC:
        handlers.append({"names": [name] + list(aliases), "function": func})
        logger.success(f"成功注册超管指令: {name}")
        return func

    return _


def get_handler_function(name: str) -> Optional[HANDLE_FUNC]:
    """
    通过名称获取处理函数

    Args:
        name (str): 子命令

    Returns:
        Optional[HANDLE_FUNC]: 函数
    """
    for handler in handlers:
        if name in handler["names"]:
            return handler["function"]
logger.debug(type(Message))


@su.handle()
async def _(bot: Bot, event: MessageEvent, message: Message = CommandArg()) -> None:
    if not message or message[0].type != "text":
        await finish("su.need_argv", [], event.user_id)
    sub_command: str = message[0].data["text"].split(" ")[0]
    logger.debug(f"[SU] 子命令: {sub_command}")
    if not (func := get_handler_function(sub_command)):
        return
    try:
        await func(bot, event, message)
    except Exception:
        await error.report()