from nonebot.adapters.onebot.v11 import Message
from nonebot.exception import FinishedException
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11.event import GroupMessageEvent
from nonebot.log import logger
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
        logger.debug(message)
        data = json.load(
            open(
                "data/messenger.messageList.json",
                encoding="utf-8"))
        argument = message.extract_plain_text()
        # 处理信息
        if argument == "":
            await messenger.finish("Usage: messenger <收件人QQ>\n<内容>")
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
                "[信鸽]: 新任务\n"
                f"RECV: {qq}\nSENDER: {sender['user_id']}\nTEXT: {text}"
            ), group_id=ctrlGroup)
            await messenger.finish("已添加到信鸽队列", at_sender=True)

    except FinishedException:
        raise FinishedException()
    except Exception:
        await bot.send_group_msg(
            message=traceback.format_exc(),
            group_id=ctrlGroup)
        await messenger.finish("处理失败")


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
                    f"\n发信：{msg['sender']['nickname']}({msg['sender']['user_id']})\n{msg['text']}",
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
