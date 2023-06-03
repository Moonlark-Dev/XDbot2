import traceback
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Message, GroupMessageEvent
from nonebot.matcher import Matcher
from nonebot import on_command
from .su import su
from . import _error
from nonebot import get_bots
from . import _lang
import json
import time

update_notice_cache = ""


@on_command("update-notice", aliases={"un", "更新推送"}).handle()
async def _(matcher: Matcher, event: GroupMessageEvent):
    try:
        data = json.load(open("data/su.update_notice.json", encoding="utf-8"))
        if str(event.group_id) in data["disabled"]:
            data["disabled"].pop(data["disabled"].index(str(event.group_id)))
            json.dump(data, open(
                "data/su.update_notice.json", "w", encoding="utf-8"))
            await matcher.finish(_lang.text("update-notice.enabled", [], str(event.user_id)))
        else:
            data["disabled"].append(str(event.group_id))
            json.dump(data, open(
                "data/su.update_notice.json", "w", encoding="utf-8"))
            await matcher.finish(_lang.text("update-notice.disabled", [], str(event.user_id)))

    except:
        await _error.report(traceback.format_exc(), matcher)


@su.handle()
async def su_update_notice(message: Message = CommandArg()):
    try:
        argument = str(message).split(" ")
        if argument[0] in ["update-notice", "un", "updnotice"]:
            global update_notice_cache
            text = str(message)[argument[0].__len__() + 1:]
            if text == "submit":
                disabled_update_notice = json.load(
                    open("data/su.update_notice.json", encoding="utf-8"))["disabled"]
                if update_notice_cache != "":
                    multiAccoutData = json.load(
                        open("data/su.multiaccoutdata.ro.json", encoding="utf-8"))
                    groupList = list(multiAccoutData.keys())
                    bots = get_bots()
                    # 开始广播
                    for group in groupList:
                        if group in disabled_update_notice:
                            continue
                        try:
                            await bots[multiAccoutData[group]].send_group_msg(
                                message=Message(
                                    f"【XDbot2 {time.strftime('%Y-%m-%d', time.localtime())}】\n{update_notice_cache}"),
                                group_id=group,
                            )
                        except BaseException:
                            await su.send(f"在 {group} 推送更新失败：\n{traceback.format_exc()}")
                    update_notice_cache = ""
                else:
                    await su.finish("请先使用 /su un <context> 设定超级广播内容")
            elif text == "drop":
                update_notice_cache = ""
                await su.finish("更新推送广播内容已清除")
            elif text == "get":
                await su.finish(Message(update_notice_cache))
            else:
                update_notice_cache = text
                await su.finish("更新推送广播内容已设定")
    except BaseException:
        await _error.report(traceback.format_exc(), su)
