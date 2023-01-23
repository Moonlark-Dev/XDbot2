from nonebot.adapters.onebot.v11.bot import Bot
from nonebot.adapters.onebot.v11.event import GroupMessageEvent
from nonebot.adapters.onebot.v11 import Message
from nonebot.params import CommandArg
from nonebot.exception import FinishedException
from nonebot import on_command
import json
import traceback
from urllib import request as req
import urllib.error

ctrlGroup = json.load(open("data/ctrl.json", encoding="utf-8"))["control"]
linuxman = on_command("linuxman")


@linuxman.handle()
async def linuxmanHandle(bot: Bot,
                         event: GroupMessageEvent,
                         message: Message = CommandArg()):
    try:
        argument = message.extract_plain_text().split(" ")
        try:
            with req.urlopen(
                    f"https://man.archlinux.org/man/{argument[0]}.txt") as fp:
                manpage = fp.read().decode("utf-8")
                await bot.call_api(
                    api="seng_group_forward_msg",
                    messages=[{
                        "type": "node",
                        "data": {
                            "name": "XDbot2 LINUXMAN",
                            "uin": str((await
                                        bot.get_login_info())['user_id']),
                            "content": str(manpage)
                        }
                    }],
                    group=str(event.group_id))
                await linuxman.finish()
        except urllib.error.HTTPError as e:
            if e.status == 404:
                await linuxman.finish("找不到manpage")
    except FinishedException:
        raise FinishedException()
    except Exception:
        await bot.send_group_msg(message=traceback.format_exc(),
                                 group_id=ctrlGroup)
    await linuxman.finish("处理失败")


# [HELPSTART] Version: 2
# Command: linuxman
# Usage: linuxman（查看linux manpage）
# Usage: linuxman man.1（查看man(1)）
# Info: 查看linux manpage
# Msg: 查看linux manpage
# [HELPEND]
