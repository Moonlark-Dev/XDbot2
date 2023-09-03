from _utils import *
from nonebot import on_command
from nonebot.adapters.onebot.v11 import MessageEvent, GroupMessageEvent, PrivateMessageEvent, MessageSegment

whoami = on_command("whoami", aliases={"我是谁"})

@whoami.handle()
async def _(event: MessageEvent):
    await whoami.finish(MessageSegment.reply(event.message_id) + MessageSegment.text(f"{event.sender.nickname}"))