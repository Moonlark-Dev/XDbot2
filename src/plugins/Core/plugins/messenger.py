from nonebot.adapters.onebot.v11 import Message
from nonebot.exception import FinishedException
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11.event import GroupMessageEvent
# from nonebot.log import logger
from . import _error
from . import _lang
from nonebot.adapters.onebot.v11.bot import Bot
from nonebot import on_message
from nonebot import on_command
import traceback
import json

messenger = on_command("messenger", aliases={"msg", "信鸽"})
msgSender = on_message()
ctrlGroup = json.load(open("data/ctrl.json", encoding="utf-8"))["control"]


@messenger.handle()
async def messengerHandle(
        bot: Bot,
        event: GroupMessageEvent,
        message: Message = CommandArg()):
    try:
        # logger.debug(message)
        data = json.load(
            open(
                "data/messenger.messageList.json",
                encoding="utf-8"))
        argument = str(message)
        # 处理信息
        if argument == "":
            await messenger.finish(_lang.text("messenger.usage",[],event.get_user_id()))
        else:
            qq = argument.split("\n")[0]
            text1 = argument.split("\n")[1:]
            text = ""
            for t in text1:
                text += t
                text += "\n"
            sender = await bot.get_stranger_info(user_id=event.get_user_id())
            data += [{
                "recv": qq,
                "text": text,
                "sender": sender
            }]
            json.dump(data, open(
                "data/messenger.messageList.json",
                mode="w",
                encoding="utf-8"
            ))
            await bot.send_group_msg(message=(
                f"{_lang.text('messenger.new',[],event.get_user_id())}"
                f"RECV: {qq}\nSENDER: {sender['user_id']}\nTEXT: {text}"
            ), group_id=ctrlGroup)
            await messenger.finish(_lang.text("messenger.success",[],event.get_user_id()), at_sender=True)

    except FinishedException:
        raise FinishedException()
    except Exception:
        await bot.send_group_msg(
            message=traceback.format_exc(),
            group_id=ctrlGroup)
        await messenger.finish(_lang.text("messenger.error",[],event.get_user_id()))


@msgSender.handle()
async def msgSenderHandle(
        bot: Bot,
        event: GroupMessageEvent):
    try:
        data = json.load(
            open(
                "data/messenger.messageList.json",
                encoding="utf-8"))
        length = 0
        for msg in data:
            if msg["recv"] == event.get_user_id():
                await msgSender.send(
                    _lang.text("messenger.send",[msg["sender"]["nickname"],msg["sender"]["user_id"],msg["text"]],event.get_user_id()),
                    at_sender=True
                )
                data.pop(length)
            length += 1
        json.dump(
            data,
            open(
                "data/messenger.messageList.json",
                "w",
                encoding="utf-8"))
    except Exception:
        await bot.send_group_msg(
            message=traceback.format_exc(),
            group_id=ctrlGroup
        )

# [HELPSTART] Version: 2
# Command: messenger
# Info: 信使，让XDbot帮你带话
# Msg: XDbot2 信使
# Usage: messenger <收信人>\n<内容>
# [HELPEND]
