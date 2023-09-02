from nonebot.adapters.onebot.v11 import Bot, Message
from nonebot import on_command, on_message, on_keyword
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11.event import GroupMessageEvent, MessageEvent
from nonebot.adapters.onebot.v11.permission import GROUP_ADMIN, GROUP_OWNER
from nonebot.permission import SUPERUSER
from nonebot.matcher import Matcher
import traceback
import json
from . import _error as error
from . import _lang

defaultConfig = {"keywords_list": ["我是傻逼"]}
try:
    config = json.load(open("data/essencemsg.config.json", encoding="utf-8"))
except:
    config = defaultConfig.copy()
    json.dump(defaultConfig, open("data/essencemsg.config.json", "w", encoding="utf-8"))


def writeConfig(cfg):
    json.dump(cfg, open("data/essencemsg.config.json", "w", encoding="utf-8"))


configCommand = on_command("essencemsg", aliases={"essmsg"}, permission=SUPERUSER)
essencemsgCommand = on_keyword("精华", permission=GROUP_ADMIN | GROUP_OWNER | SUPERUSER)


@configCommand.handle()
async def _(
    bot: Bot,
    event: GroupMessageEvent,
    matcher: Matcher,
    message: Message = CommandArg(),
):
    try:
        args = message.extract_plain_text().split(" ")
        if args[0] == "list":
            await configCommand.finish(str(config["keywords_list"]))
        elif args[0] in ["add", "append"]:
            config["keywords_list"].append(args[1])
            writeConfig(config)
            await configCommand.finish(
                _lang.text("essencemsg.keyword.added", [args[1]], event.get_user_id())
            )
        elif args[0] in ["remove", "delete", "rm"]:
            config["keywords_list"].remove(args[1])
            writeConfig(config)
            await configCommand.finish(
                _lang.text("essencemsg.keyword.removed", [args[1]], event.get_user_id())
            )
    except BaseException:
        await error.report(traceback.format_exc(), matcher, event)


@essencemsgCommand.handle()
async def _(bot: Bot, event: GroupMessageEvent, matcher: Matcher):
    try:
        await bot.call_api("set_essence_msg", message_id=event.reply.message_id)
    except:
        await error.report(traceback.format_exc(), matcher, event, False)


@on_message().handle()
async def _(bot: Bot, matcher: Matcher, event: MessageEvent):
    try:
        message = event.get_message()
        msg = message.extract_plain_text()
        for word in config["keywords_list"]:
            if word in msg:
                await bot.call_api("set_essence_msg", message_id=event.message_id)
                break
    except BaseException:
        await error.report(traceback.format_exc(), matcher, event, feedback=False)
