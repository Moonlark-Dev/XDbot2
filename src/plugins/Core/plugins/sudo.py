from ._utils import *
from nonebot.message import event_preprocessor
from .su import su


@event_preprocessor
async def sudo_command(event: MessageEvent):
    for command_start in Json("init.json")["config"]["command_start"]:
        if event.get_plaintext().startswith(command_start + "sudo"):
            if event.user_id in Json("sudo/sudoers.json").get("sudoers", []):
                event.user_id = int(event.get_plaintext().strip().split(" ")[1].replace("[CQ:at,qq=", "").replace("]", ""))
                event.message[0].data["text"] = " ".join(
                    event.message[0].data["text"].split(" ")[2:]
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
