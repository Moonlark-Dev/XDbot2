from typing import Literal, Optional
from nonebot import get_driver
from ._utils import *

command_start = ""

# [HELPSTART] Version: 2
# Command: help
# Info: 获取帮助
# Msg: 获取帮助
# Usage: help：获取指令列表
# Usage: help <command>：获取指令帮助
# [HELPEND]

@get_driver().on_startup
async def _():
    global command_start
    command_start = Json("init.json")["config"]["command_start"][0]


def get_command_status(status: Optional[bool]) -> str:
    return {True: "√", False: "X", None: "O"}[status]

async def get_help_list(bot: Bot, event: MessageEvent) -> None:
    data = Json("help.json")
    node = await generate_node_message(bot, [
        lang.text("help.list", [
            "\n".join([
                lang.text("help.list_item", [
                    get_command_status((command := data[name])["status"]),
                    name,
                    command["msg"]
                ], event.user_id) for name in data.keys()
            ]),
            command_start
        ], event.user_id),
        lang.text("help.command_status", [], event.user_id),
        lang.text("help.eula", [], event.user_id),
        lang.text("help.copyright", [], event.user_id)
    ])
    await send_node_message(bot, node, event)


async def get_command_help(command: str, user_id: int) -> None:
    await finish("help.info", [
        get_command_status((data := Json("help.json")[command])["status"]),
        command,
        data["info"],
        "\n".join([f"{command_start}{usage}" for usage in data["usage"]])
    ], user_id, False, True)

@create_command("help")
async def _(bot: Bot, event: MessageEvent, message: Message) -> None:
    argv = message.extract_plain_text()
    if not argv:
        await get_help_list(bot, event)
        return
    try:
        await get_command_help(
            argv,
            event.user_id
        )
    except TypeError:
        await finish(
            "help.unknown_command",
            [argv],
            event.user_id
        )

