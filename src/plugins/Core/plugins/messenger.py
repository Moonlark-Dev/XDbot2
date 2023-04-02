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
    bot: Bot, event: GroupMessageEvent, message: Message = CommandArg()
):
    try:
        # logger.debug(message)
        data = json.load(
            open("data/messenger.messageList.json", encoding="utf-8"))
        argument = str(message)
        # 处理信息
        if argument == "":
            await messenger.finish(
                _lang.text("messenger.usage", [], event.get_user_id())
            )
        else:
            qq = (
                argument.split("\n")[0]
                .replace("\r", " ")
                .replace("[CQ:at,qq=", "")
                .replace("]", "")
                .strip()
            )
            text = "\n".join(argument.split("\n")[1:])
            sender = await bot.get_stranger_info(user_id=event.get_user_id())
            data += [{"recv": qq, "text": text, "sender": sender}]
            json.dump(
                data,
                open("data/messenger.messageList.json", "w", encoding="utf-8"),
            )
            await bot.send_group_msg(
                message=(
                    "[信鸽] 收到新任务：\n" f"收件：{qq}\n发件：{sender['user_id']}\n内容：{text}"),
                group_id=ctrlGroup,
            )
            await messenger.finish(
                _lang.text("messenger.success", [], event.get_user_id()), at_sender=True
            )

    except FinishedException:
        raise FinishedException()
    except Exception:
        await _error.report(traceback.format_exc(), messenger)


@msgSender.handle()
async def msgSenderHandle(bot: Bot, event: GroupMessageEvent):
    try:
        data = json.load(
            open("data/messenger.messageList.json", encoding="utf-8"))
        length = 0
        for msg in data:
            if msg["recv"] == event.get_user_id():
                await msgSender.send(
                    Message(
                        _lang.text(
                            "messenger.send",
                            [
                                msg["sender"]["nickname"],
                                msg["sender"]["user_id"],
                                msg["text"],
                            ],
                            event.get_user_id(),
                        )
                    ),
                    at_sender=True,
                )
                data.pop(length)
            length += 1
        json.dump(data, open(
            "data/messenger.messageList.json", "w", encoding="utf-8"))
    except Exception:
        await _error.report(traceback.format_exc())


# [HELPSTART] Version: 2
# Command: messenger
# Info: 信鸽
# Msg: 信鸽
# Usage: messenger <收信人>\n<内容>
# [HELPEND]
