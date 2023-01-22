from nonebot import on_command
report = on_command("report", aliases={"反馈"})
@report.handle()
async def handle():
    await report.finish("如果发现bug，请去Github提交反馈：https://github.com/This-is-XiaoDeng/XDbot2/issues", at_sender=True)
