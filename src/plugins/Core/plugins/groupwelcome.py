from nonebot.adapters.onebot.v11 import GroupIncreaseNoticeEvent, Bot,Message
from nonebot import on_notice, on_command
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11.event import GroupMessageEvent
from nonebot.permission import SUPERUSER
from nonebot.matcher import Matcher
import traceback
import json
from . import _error as error
from . import _lang
import httpx
async def getAcceptedQQList():
    async with httpx.AsyncClient() as client:
        r = (await client.get('https://api.github.com/repos/ITCraftDevelopmentTeam/Forum/issues/14/comments')).json()
        return [i['body'].replace("\n","") for i in r]

defaultConfig = {
    "welcome_global_enabled": True,
    "welcome_enabled_group": [],
    "application_check_enabled_group":[701257458],
    "welcome_message":"欢迎加入本群，我是由 IT Craft Development Team 开发的机器人 XDbot2，使用 /help 查看命令帮助",
    "application_approve_message":"您已通过 IT Craft Development Team 的加入申请",
    "application_notfound_message":"警告：您没有在 GitHub 上提交(或被通过)加入申请"
}
try:
    config = json.load(open("data/groupwelcome.config.json", encoding="utf-8"))
except:
    config = defaultConfig.copy()
    json.dump(defaultConfig, open("data/groupwelcome.config.json", "w", encoding="utf-8"))
def writeConfig(cfg):
    json.dump(cfg, open("data/groupwelcome.config.json", "w", encoding="utf-8"))
configCommand = on_command("groupwelcome", permission=SUPERUSER)
@configCommand.handle()
async def _(bot: Bot, event: GroupMessageEvent, matcher: Matcher, message: Message = CommandArg()):
    try:
        args = message.extract_plain_text()
        if args == "":
            if event.group_id in config["welcome_enabled_group"]:
                config["welcome_enabled_group"].remove(event.group_id)
                writeConfig(config)
                await configCommand.finish(_lang.text("groupwelcome.group.disabled",[],event.get_user_id))
            else:
                config["welcome_enabled_group"].append(event.group_id)
                writeConfig(config)
                await configCommand.finish(_lang.text("groupwelcome.group.enabled",[],event.get_user_id))
        else:
            args = args.split(" ")
            if args[0] == "global":
                if config["welcome_global_enabled"]:
                    config["welcome_global_enabled"] = False
                    writeConfig(config)
                    await configCommand.finish(_lang.text("groupwelcome.global.disabled",[],event.get_user_id))
                else:
                    config["welcome_global_enabled"] = True
                    writeConfig(config)
                    await configCommand.finish(_lang.text("groupwelcome.global.enabled",[],event.get_user_id))
            elif args[0] == "application":
                if event.group_id in config["application_check_enabled_group"]:
                    config["application_check_enabled_group"].remove(event.group_id)
                    writeConfig(config)
                    await configCommand.finish(_lang.text("groupwelcome.application.disabled",[],event.get_user_id))
                else:
                    config["application_check_enabled_group"].append(event.group_id)
                    writeConfig(config)
                    await configCommand.finish(_lang.text("groupwelcome.application.enabled",[],event.get_user_id))
            elif args[0] in ["welcome_message","wm"]:
                config["welcome_message"] = args[1]
                writeConfig(config)
                await configCommand.finish(_lang.text("groupwelcome.message.wm.edited",[args[1]],event.get_user_id))
            elif args[0] in ["application_approve_message","aam"]:
                config["application_approve_message"] = args[1]
                writeConfig(config)
                await configCommand.finish(_lang.text("groupwelcome.message.aam.edited",[args[1]],event.get_user_id))
            elif args[0] in ["application_notfound_message", "anm"]:
                config["application_notfound_message"] = args[1]
                writeConfig(config)
                await configCommand.finish(_lang.text("groupwelcome.message.anm.edited",[args[1]],event.get_user_id))
            elif args[0] == "confirm_reset_config":
                writeConfig(defaultConfig)
                await configCommand.finish(_lang.text("groupwelcome.reset_config",[],event.get_user_id))
            elif args[0] in ["application_approved_list","aal"]:
                await configCommand.finish(str(await getAcceptedQQList()))
    except BaseException:
        await error.report(traceback.format_exc(), matcher, event)
GroupIncrease = on_notice()
@GroupIncrease.handle()
async def _(bot: Bot, event: GroupIncreaseNoticeEvent, matcher: Matcher):
    try:
        if event.group_id in config["welcome_enabled_group"] or config["welcome_global_enabled"]:
            await GroupIncrease.send(config["welcome_message"],at_sender=True)
        if event.group_id in config["application_check_enabled_group"]:
            if str(event.user_id) in await getAcceptedQQList():
                await GroupIncrease.finish(config["application_approve_message"],at_sender=True)
            else:
                await GroupIncrease.finish(config["application_notfound_message"],at_sender=True)
        GroupIncrease.finish()
    except BaseException:
        await error.report(traceback.format_exc(), matcher, event)