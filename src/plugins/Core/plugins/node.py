# 麻烦pr个本地化，termux 写累死了
from nonebot import on_command
from nonenot.matcher import Matcher
from . import _error
from nonebot.message import event_preprocessor
from ._utils import Json
from nonebot import get_driver

try:
    node_id = get_driver().config.node_id
except:
    node_id = "DEFAULT"
 
@on_command("node-info").handle()
async def nodeinfohandler(matcher: Matcher):
    await matcher.finish(f"节点ID：{node_id}")


