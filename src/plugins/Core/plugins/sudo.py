from ._utils import *
from nonebot.message import event_preprocessor

@event_preprocessor
async def sudo_command(event: MessageEvent):
    for command_start in Json("init.json")["config"]["command_start"]:
        if event.get_plaintext().startswith(command_start + "sudo"):
            if event.user_id in Json("sudo/sudoers.json").get("sudoers", []):
                event.user_id = int(event.get_plaintext().strip().split(" ")[1])
                event.message[0].data["text"] = " ".join(
                    event.message[0].data["text"].split(" ")[2:])
