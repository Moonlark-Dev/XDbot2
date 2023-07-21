
from nonebot.exception import IgnoredException
from nonebot.message import event_preprocessor
from nonebot.adapters.onebot.v11.permission import GROUP_ADMIN
from . import _error as error
from . import _lang as lang
import os
from nonebot import on_command
from ._utils import Json
from nonebot.matcher import Matcher
from nonebot.adapters import MessageEvent
from nonebot.adapters.onebot.v11 import GroupMessageEvent
from nonebot.adapters import Message
from nonebot.params import CommandArg


@on_command("update", aliases={"检查更新"}).handle()
async def update_xdbot(matcher: Matcher, event: MessageEvent):
    try:
        await matcher.send(lang.text("update.checking", [], event.get_user_id()))
        old_commit = os.popen("git log").read().split("\n")[0].split(" ")[1][:7]
        os.system("python3 update.py")
        await matcher.finish(lang.text(
            "update.finish",
            [
                old_commit,
                os.popen("git log").read().split("\n")[0].split(" ")[1][:7]
            ],
            event.get_user_id()
        ))
    except BaseException:
        await error.report()


@on_command("checkout", permission=GROUP_ADMIN).handle()
async def checkout_xdbot(matcher: Matcher, event: GroupMessageEvent, node: Message = CommandArg()):
    try:
        if node.extract_plain_text() == "develop":
            Json("node_manager.enabled_groups.json").get("groups", []).append(event.group_id)
            await matcher.finish(lang.text("node_manager.enabled", [], event.user_id))
        else:
            try:
                Json("node_manager.enabled_groups.json").get("groups", []).pop(
                    Json("node_manager.enabled_groups.json").get("groups", []).index(event.group_id)
                )
            except IndexError:
                pass
            await matcher.finish(lang.text("node_manager.disabled", [], event.user_id))
    except:
        await error.report()


@event_preprocessor
async def _(event: GroupMessageEvent):
    try:
        if event.group_id not in Json("node_manager.enabled_groups.json").get("groups", []):
            raise IgnoredException("多节点：未启用 DEVELOP 节点")

    except IgnoredException as e:
        raise IgnoredException(e)
    except Exception:
        await error.report()
