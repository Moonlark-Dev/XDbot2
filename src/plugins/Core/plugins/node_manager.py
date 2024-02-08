# [DEVELOP]

from nonebot.exception import IgnoredException
from nonebot.message import event_preprocessor
from nonebot.adapters.onebot.v11.permission import GROUP_ADMIN, GROUP_OWNER
from nonebot.permission import SUPERUSER
from . import _error as error
from . import _lang as lang
import os
from nonebot import on_command
from ._utils import *
from nonebot.matcher import Matcher
from nonebot.adapters.onebot.v11 import MessageEvent
from nonebot.adapters.onebot.v11 import GroupMessageEvent
from nonebot.adapters import Message
from nonebot.params import CommandArg
import subprocess

# from .su import su
from . import _error

# from nonebot.adapters import Message
# from nonebot.params import CommandArg
from .etm import bag

try:
    json = __import__("json5")
except:
    import json

give = on_command("give")


@give.handle()
async def _(event: GroupMessageEvent, message: Message = CommandArg()):
    try:
        args = str(message).strip().split(" ")
        args.insert(0, "give")

        if args[0] in ["give", "给"]:
            bag.add_item(
                args[1].replace("[CQ:at,qq=", "").replace("]", ""),
                args[2],
                int(args[3]) if len(args) >= 4 and args[3][0] != "{" else 1,
                json.loads(" ".join(args[4:]) if len(args) >= 5 else "{}"),
            )
            await give.finish("完成！")
    except:
        await _error.report()


@on_command("update", aliases={"检查更新"}).handle()
async def update_xdbot(matcher: Matcher, event: MessageEvent):
    try:
        await matcher.send(lang.text("update.checking", [], event.get_user_id()))
        await matcher.finish(os.popen("git pull").read())
    except BaseException:
        await error.report()


# [HELPSTART] Version: 2
# Command: switch
# Usage: switch {develop|master}
# Msg: 切换节点
# Info: 切换 XDbot2 节点（详见 node(0)）
# [HELPEND]


@on_command(
    "checkout", aliases={"switch"}, permission=GROUP_ADMIN | GROUP_OWNER | SUPERUSER
).handle()
async def checkout_xdbot(
    matcher: Matcher, event: GroupMessageEvent, node: Message = CommandArg()
):
    try:
        if node.extract_plain_text().startswith("develop"):
            Json("node_manager.groups.json")[str(event.group_id)] = True
            await matcher.finish(lang.text("node_manager.enabled", [], event.user_id))
        else:
            Json("node_manager.groups.json")[str(event.group_id)] = None
            await matcher.finish(lang.text("node_manager.disabled", [], event.user_id))
    except:
        await error.report()


@create_command("cb", aliases={"change-branch"}, permission=SUPERUSER)
async def change_branch(_bot, _event, _message, matcher: Matcher = Matcher()):
    message = _message.extract_plain_text()
    commands = [
        ["git", "fetch", "origin"],
        ["git", "checkout", message],
        ["git", "pull", "origin", message],
    ]
    for cmd in commands:
        output = subprocess.Popen(cmd, stdout=subprocess.PIPE).communicate()[0]
        await matcher.send(output.decode("utf-8"))


@event_preprocessor
async def _(event: GroupMessageEvent):
    try:
        if event.get_plaintext()[1:].startswith("checkout"):
            return
        if not Json("node_manager.groups.json").get(str(event.group_id), None):
            raise IgnoredException("多节点：未启用 DEVELOP 节点")

    except IgnoredException as e:
        raise IgnoredException(e)
    except Exception:
        await error.report()
