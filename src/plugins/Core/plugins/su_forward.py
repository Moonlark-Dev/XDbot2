import traceback
from nonebot.adapters.onebot.v11 import Bot
from nonebot.adapters.onebot.v11 import Message
from nonebot.matcher import Matcher
from nonebot.params import CommandArg
from .su import su
from . import _error
from . import forward
import json


@su.handle()
async def set_forward(matcher: Matcher, bot: Bot, message: Message = CommandArg()):
    try:
        argument = message.extract_plain_text().split(" ")
        if argument[0] == "forward" or argument[0] == "消息转发":
            data = json.load(open("data/forward.groupList.json", encoding="utf-8"))
            if argument[1] == "add" or argument[1] == "添加群":
                data += [argument[2]]
                try:
                    await bot.set_group_card(
                        group_id=int(argument[2]),
                        user_id=(await bot.get_login_info())["user_id"],
                        card=(await bot.get_login_info())["nickname"] + "（监听中）",
                    )
                except BaseException:
                    pass
            elif argument[1] == "remove" or argument[1] == "删除群":
                length = 0
                for group in data:
                    if group == argument[2]:
                        data.pop(length)
                        try:
                            await bot.set_group_card(
                                group_id=int(argument[2]),
                                user_id=(await bot.get_login_info())["user_id"],
                                card=(await bot.get_login_info())["nickname"][:-5],
                            )
                        except BaseException:
                            pass

                    else:
                        length += 1
            await matcher.send("完成")
            json.dump(data, open("data/forward.groupList.json", "w", encoding="utf-8"))
            forward.forwardData = json.load(
                open("data/forward.groupList.json", encoding="utf-8")
            )

    except BaseException:
        await _error.report(traceback.format_exc(), matcher)
