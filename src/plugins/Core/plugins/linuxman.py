from nonebot.adapters.onebot.v11.bot import Bot
from nonebot.adapters.onebot.v11.event import GroupMessageEvent
from nonebot.adapters.onebot.v11 import Message
from nonebot.params import CommandArg
from nonebot.exception import FinishedException
from nonebot import on_command
from nonebot.exception import ActionFailed
import json
from . import _error
from . import _lang
import traceback
import httpx

ctrlGroup = json.load(open("data/ctrl.json", encoding="utf-8"))["control"]
linuxman = on_command("linuxman")


@linuxman.handle()
async def linuxmanHandle(
    bot: Bot, event: GroupMessageEvent, message: Message = CommandArg()
):
    try:
        argument = message.extract_plain_text()
        async with httpx.AsyncClient() as client:
            req = await client.get(f"https://man.archlinux.org/man/{argument}.txt")
            text = req.read().decode("utf-8")
        if req.status_code == 404:
            await linuxman.finish(_lang.text("linuxman.error", [], event.get_user_id()))
        try:
            await linuxman.finish(text)
        except ActionFailed:
            text = text.split("\n\n")
            msg = []
            qq = str((await bot.get_login_info())["user_id"])
            nowLen = 0
            for t in text:
                msg.append(
                    {
                        "type": "node",
                        "data": {
                            "uin": qq,
                            "name": "XDBOT2 LINUX MAN",
                            "content": t.strip(),
                        },
                    }
                )
            nowLen = 0
            for _ in range(len(msg) // 99 + 1):
                nowLen += 99
                await bot.call_api(
                    api="send_group_forward_msg",
                    messages=msg[nowLen - 99 : nowLen],
                    group_id=str(event.group_id),
                )
            await linuxman.finish(
                _lang.text("linuxman.finish", [], event.get_user_id())
            )
    except FinishedException:
        raise FinishedException()
    except Exception:
        await _error.report(traceback.format_exc(), linuxman)


# [HELPSTART] Version: 2
# Command: linuxman
# Usage: linuxman：查看linux manpage
# Usage: linuxman man.1：查看man(1)
# Info: 查看linux manpage
# Msg: 查看manpage
# [HELPEND]
