import re
from nonebot import on_command, on_message
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message
from nonebot.exception import FinishedException
from nonebot.params import CommandArg
import json
from . import _smart_reply as _
from . import _lang as lang
from . import _error
import traceback
import random

reply = on_command("reply", aliases={"调教"})
reply_sender = on_message()

@reply_sender.handle()
async def reply_sender_handle(event: GroupMessageEvent):
    try:
        data = _.get_list()
        message = str(event.get_message())
        user_id = event.get_user_id()
        for item in list(data.values()):
            if item["global"] or item["group_id"] == event.group_id or item["user_id"] == user_id:
                if re.match(item["matcher"], message):
                    await reply_sender.send(Message(random.choice(item["text"])))
    except BaseException:
        await _error.report(traceback.format_exc())

# [HELPSTART] Version: 2
# Command: reply
# Info: 调教XDbot
# Msg: 调教XDbot
# Usage: reply
# Usage: reply remove <ID>
# Usage: reply add <正则表达式>\n<回复内容1>\n[回复内容2]\n[...]
# [HELPEND]

@reply.handle()
async def reply_command(event: GroupMessageEvent, message: Message = CommandArg()):
    try:
        msg = str(message).replace("&#91", "[").replace("&#93;", "]")
        arguments = msg.split("\n")[0].split(" ")
        user_id = event.get_user_id()
        if arguments[0] == "":
            await reply.finish(lang.text("reply.need_argv", [], user_id))
        elif arguments[0] == "add":
            matcher = arguments[1]
            reply_text = msg.split("\n")[1:]
            reply_id = await _.create_reply(matcher, reply_text, event.group_id, user_id)
            await reply.finish(lang.text("reply.add_finish", [str(reply_id)], user_id))
        elif arguments[0] == "remove":
            if _.remove_reply(arguments[0], user_id):
                await reply.finish(lang.text("reply.finish", [], user_id))
            else:
                await reply.finish(lang.text("reply.403", [], user_id))
        elif arguments[0] == "get":
            await reply.finish(json.dumps(_.get_list()[arguments[1]]))
            

    except IndexError:
        await reply.finish(lang.text("reply.need_argv", [], event.get_user_id()))
    except FinishedException:
        raise FinishedException()
    except BaseException:
        await _error.report(traceback.format_exc(), reply)

