import os

from nonebot import on_command
from nonebot.matcher import Matcher


@on_command("update", aliases={"检查更新"}).handle()
async def _(matcher: Matcher):
    await matcher.send("正在运行更新程序，请稍候 ...")
    old_branch = os.popen("git log").read().split("\n")[
        0].split(" ")[1][:7]
    os.system("python3 update.py")
    await matcher.send('旧提交：%s\n新提交：%s' % (old_branch, os.popen("git log").read().split("\n")[0].split(" ")[1][:7]))
