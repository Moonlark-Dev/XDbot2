from nonebot import on_command
from nonebot.adapters.onebot.v11 import Message, MessageEvent
from nonebot.params import CommandArg
from . import _lang
from . import _error

report = on_command("report", aliases={"举报"})


@report.handle()
async def handle(event: MessageEvent, message: Message = CommandArg()):
    await _error.report(
        Message((
            "「举报信息」\n"
            f"{message}\n"
            f"{event.get_session_id()}\n")))
    await report.finish(
        _lang.text("report.success", [], event.get_user_id()), at_sender=True)

# [HELPSTART] Version: 2
# Command: report
# Usage: /report <messages>
# Msg: 举报其他用户
# Info: 用于举报其他用户（或自己）的违规行为
# [HELPEND]
