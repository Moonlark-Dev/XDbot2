from nonebot.exception import IgnoredException
from nonebot.adapters.onebot.v11.permission import _group_admin, _group_owner, GROUP_ADMIN, GROUP_OWNER
from nonebot import get_driver
from nonebot.message import event_preprocessor
from ._utils import *
from nonebot.matcher import matchers

def get_matchers() -> list[type[Matcher]]:
    _matchers = []
    for matcher in matchers.provider[1]:
        # print(matcher.type)
        if matcher.type == "message":
            _matchers.append(matcher)
    return _matchers

def get_commands() -> list[tuple[str]]:
    _matchers = get_matchers()
    commands = []
    for matcher in _matchers:
        if len(matcher.rule.checkers) <= 0:
            continue
        if not hasattr(list(matcher.rule.checkers)[0].call, "cmds"):
            continue
        command_aliases = []
        for item in list(matcher.rule.checkers)[0].call.cmds:
            command_aliases.append(item[0])
        commands.append(command_aliases)
    return commands

def search_command_by_name(name: str) -> tuple[str] | tuple[()]:
    for command in get_commands():
        for cmd_aliases in command:
            if name == cmd_aliases:
                return command
    return ()

def is_msg_call_blocked_cmd(message: str, blocked_command: list[str]) -> bool:
    for command_start in get_driver().config.command_start:
        for command in blocked_command:
            if message.startswith(f"{command_start}{command}"):
                return True
    return False

def get_blocked_commands(group_id: int) -> list[str]:
    blocked_command = []
    for command in Json(f"command_manager/{group_id}.json").get("blocked_command", []):
        blocked_command += list(search_command_by_name(command))
    return blocked_command

@event_preprocessor
async def block_blocked_command(event: GroupMessageEvent) -> None:
    if event.get_user_id() in get_driver().config.superusers\
            or await _group_admin(event)\
            or await _group_owner(event):
        return
    if is_msg_call_blocked_cmd(event.get_plaintext(), get_blocked_commands(event.group_id)):
        raise IgnoredException("命令管理器：被禁用")
    
def is_command_blocked(command: str, group_id: int) -> bool:
    return command in get_blocked_commands(group_id)

def is_command_valid(command_name: str) -> bool:
    for command_aliases in get_commands():
        if command_name in command_aliases:
            return True
    return False

def can_block_command(command_name: str, group_id: int) -> bool:
    return (not is_command_blocked(command_name, group_id)) and is_command_valid(command_name)

def can_unblock_command(command_name: str, group_id: int) -> bool:
    return is_command_blocked(command_name, group_id) and is_command_valid(command_name)

def block_command(command_name: str, group_id: int) -> bool:
    if not can_block_command(command_name, group_id):
        return FAILED
    Json(f"command_manager/{group_id}.json").append_to(command_name, "blocked_command")
    return SUCCESS

def is_same_command(command1: str, command2: str) -> bool:
    return search_command_by_name(command1) == search_command_by_name(command2)

def unblock_command(command_name: str, group_id: int):
    if not can_unblock_command(command_name, group_id):
        return FAILED
    blocked_commands: list = Json(f"command_manager/{group_id}.json").get("blocked_command", [])
    for command in blocked_commands:
        if is_same_command(command, command_name):
            blocked_commands.pop(blocked_commands.index(command))
    Json(f"command_manager/{group_id}.json")["blocked_command"] = blocked_commands
    return SUCCESS

@on_command("cm", aliases={"command-manager", "command"}, permission=SUPERUSER | GROUP_ADMIN | GROUP_OWNER).handle()
async def handle_cm_command(matcher: Matcher, event: GroupMessageEvent, message: Message = CommandArg()):
    try:
        argv = message.extract_plain_text().split(" ")
        match argv[0]:
            case "block":
                if block_command(argv[1], event.group_id):
                    await finish("cm.blocked", [argv[1]], event.user_id)
                else:
                    await finish("cm.block_failed", [argv[1]], event.user_id)
            case "unblock":
                if unblock_command(argv[1], event.group_id):
                    await finish("cm.unblocked", [argv[1]], event.user_id)
                else:
                    await finish("cm.unblock_failed", [argv[1]], event.user_id)
            case "list" | "":
                await finish("cm.blocked_command_list", [
                    " ".join(Json(f"command_manager/{event.group_id}.json").get("blocked_command", []))
                ], event.user_id)
    except:
        await error.report()
    
# [HELPSTART] Version: 2
# Command: cm
# Msg: 命令管理器
# Info: 在群内禁用、启用命令 [*superuser *group_admin *group_owner *group]
# Usage: cm block <命令>：禁用命令
# Usage: cm unblock <命令>：启用命令
# Usage: cm list：查看被禁用的命令
# [HELPEND]
    
    
    