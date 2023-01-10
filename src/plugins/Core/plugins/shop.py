import json
from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, Message
from nonebot.params import CommandArg
from . import _userCtrl

ctrlGroup = json.load(open("data/ctrl.json", encoding="utf-8"))["control"]
shop = on_command("shop", aliases={"商店"})


@shop.handle()
async def shopHandle(
        bot: Bot,
        event: GroupMessageEvent,
        message: Message = CommandArg()):...
