from nonebot import on_command
from nonebot.adapters.onebot.v11 import MessageEvent
from . import _lang
report = on_command("report", aliases={"反馈"})


@report.handle()
async def handle(event: MessageEvent):
    await report.finish(_lang.text("report.github",[],event.get_user_id()), at_sender=True)
