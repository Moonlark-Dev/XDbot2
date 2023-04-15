import traceback
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Message
from .su import su
from . import _error
from nonebot import get_bots
import json

su_notice_cache = ""


@su.handle()
async def su_primary_notice(message: Message = CommandArg()):
    try:
        argument = str(message).split(" ")
        if argument[0] == "notice" or argument[0] == "超级广播" or argument[0] == "广播":
            global su_notice_cache
            text = str(message)[argument[0].__len__() + 1:]
            if text == "submit":
                if su_notice_cache != "":
                    multiAccoutData = json.load(
                        open("data/su.multiaccoutdata.ro.json", encoding="utf-8"))
                    groupList = list(multiAccoutData.keys())
                    bots = get_bots()
                    # 开始广播
                    for group in groupList:
                        try:
                            await bots[multiAccoutData[group]].send_group_msg(
                                message=Message(f"【超级广播】\n{su_notice_cache}"),
                                group_id=group,
                            )
                        except BaseException:
                            await su.send(f"在 {group} 广播消息失败：\n{traceback.format_exc()}")
                    su_notice_cache = ""
                else:
                    await su.finish("请先使用 /su notice <context> 设定超级广播内容")
            elif text == "drop":
                su_notice_cache = ""
                await su.finish("超级广播内容已清除")
            elif text == "get":
                await su.finish(Message(su_notice_cache))
            else:
                su_notice_cache = text
                await su.finish("超级广播内容已设定")
    except BaseException:
        await _error.report(traceback.format_exc(), su)
