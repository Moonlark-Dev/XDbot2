from ._utils import *
from nonebot.message import event_preprocessor
from .su import su
import json


@event_preprocessor
async def sudo_command(bot: Bot, event: MessageEvent):
    for command_start in Json("init.json")["config"]["command_start"]:
        if event.get_plaintext().startswith(command_start + "sudo"):
            if event.user_id in Json("sudo/sudoers.json").get("sudoers", []):
                need_change = Json("sudo.config.json").get("change_sender", True)
                replace_user_id = int(
                    str(event.get_message())
                    .strip()
                    .split(" ")[1]
                    .replace("[CQ:at,qq=", "")
                    .replace("]", "")
                )
                event.user_id = replace_user_id
                event.sender.user_id = replace_user_id
                if need_change:
                    if isinstance(event, GroupMessageEvent):
                        user_info = json.loads(await bot.get_group_member_info(group_id=event.group_id, user_id=replace_user_id))
                        event.sender.age = user_info['age']
                        event.sender.level = user_info['level']
                        event.sender.sex = user_info['sex']
                        event.sender.nickname = user_info['nickname']
                        event.sender.area = user_info['area']
                        event.sender.card = user_info['card']
                        event.sender.role = user_info['role']
                    else:
                        user_info = json.loads(await bot.get_stranger_info(user_id=replace_user_id, no_cache=True))
                        event.sender.age = user_info['age']
                        event.sender.level = user_info['level']
                        event.sender.sex = user_info['sex']
                        event.sender.nickname = user_info['nickname']
                event.message = Message(
                    " ".join(str(event.get_message()).split(" ")[2:])
                )


@su.handle()
async def su_sudo(message: Message = CommandArg()):
    try:
        argument = str(message).split(" ")
        if argument[0] in ["sudoers"]:
            sudoers: list = Json("sudo/sudoers.json").get("sudoers")
            match argument[1]:
                case "add":
                    sudoers.append(int(argument[2]))
                case "remove":
                    sudoers.pop(sudoers.index(int(argument[2])))
            Json("sudo/sudoers.json")["sudoers"] = list(set(sudoers))
    except:
        await error.report()
