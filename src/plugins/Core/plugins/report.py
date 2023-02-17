from nonebot import on_command
from nonebot.adapters.onebot.v11 import Message, MessageEvent
from nonebot.params import CommandArg
from . import _lang
from . import _error

report = on_command("report", aliases={"反馈"})


@report.handle()
async def handle(event: MessageEvent, message: Message = CommandArg()):
    await _error.report(("「新反馈」\n"
        f"{message}\n"
        f"{event.get_session_id()}\n"))
    await report.finish(
        _lang.text("report.github", [], event.get_user_id()), at_sender=True)
