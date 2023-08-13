from nonebot.exception import IgnoredException
from nonebot.message import event_preprocessor
from nonebot.adapters.onebot.v11.permission import GROUP_ADMIN, GROUP_OWNER
from nonebot.permission import SUPERUSER
from . import _error as error
from . import _lang as lang
import os
from nonebot import on_command
from ._utils import Json
from nonebot.matcher import Matcher
from nonebot.adapters.onebot.v11 import MessageEvent
from nonebot.adapters.onebot.v11 import GroupMessageEvent
from nonebot.adapters import Message
from nonebot.params import CommandArg

# from .su import su
from . import _error

# from nonebot.adapters import Message
# from nonebot.params import CommandArg
from .etm import bag

try:
    import json5 as json
except:
    import json

give = on_command("give")


@give.handle()
async def _(event: GroupMessageEvent, message: Message = CommandArg()):
    try:
        args = str(message).strip().split(" ")
        args.insert(0, str(event.user_id))
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
        old_commit = os.popen("git log").read().split("\n")[0].split(" ")[1][:7]
        os.system("python3 update.py")
        await matcher.finish(
            lang.text(
                "update.finish",
                [
                    old_commit,
                    os.popen("git log").read().split("\n")[0].split(" ")[1][:7],
                ],
                event.get_user_id(),
            )
        )
    except BaseException:
        await error.report()


# [HELPSTART] Version: 2
# Command: checkout
# Usage: checkout
# Msg: 切换 XDbot2 节点
# Info: 切换 XDbot2 节点（详见 node(0)）


@on_command("checkout", permission=GROUP_ADMIN | GROUP_OWNER | SUPERUSER).handle()
async def checkout_xdbot(
    matcher: Matcher, event: GroupMessageEvent, node: Message = CommandArg()
):
    try:
        if node.extract_plain_text() == "develop":
            Json("node_manager.groups.json")[str(event.group_id)] = True
            await matcher.finish(lang.text("node_manager.enabled", [], event.user_id))
        else:
            Json("node_manager.groups.json")[str(event.group_id)] = None
            await matcher.finish(lang.text("node_manager.disabled", [], event.user_id))
    except:
        await error.report()


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
