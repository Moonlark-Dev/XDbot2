from nonebot.adapters.onebot.v11 import MessageEvent
from nonebot.matcher import Matcher
from nonebot.adapters import Message
from nonebot.params import CommandArg
from ..plugins.su import su
from ..plugins import _smart_reply as smart_reply
from ..plugins import _error


@su.handle()
async def _(matcher: Matcher, event: MessageEvent, message: Message = CommandArg()):
    try:
        argument = str(message).split(" ")
        if argument[0] in ["reply", "调教"]:
            if argument[1] in ["global"]:
                reply_id = argument[2]
                smart_reply.global_reply(reply_id)
                await matcher.finish("完成")
            elif argument[1] in ["remove", "rm", "删除"]:
                smart_reply.remove_reply(argument[2], event.get_user_id(), True)
                await matcher.finish("完成")
    except:
        await _error.report()
