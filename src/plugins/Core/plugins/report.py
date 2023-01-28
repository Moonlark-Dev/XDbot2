from nonebot import on_command
report = on_command("report", aliases={"反馈"})


@report.handle()
async def handle():
    await report.finish("如果阁下发现了不得了的事情，千万不要去Github提交issue哦！！https://github.com/This-is-XiaoDeng/XDbot2/issues", at_sender=True)
