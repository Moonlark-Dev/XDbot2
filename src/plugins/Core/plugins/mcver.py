from nonebot_plugin_apscheduler import scheduler
import traceback
from nonebot.adapters import Event
from nonebot import on_command, require, get_bot
# from .account import multiAccoutData
import httpx
from nonebot.adapters.onebot.v11 import GroupMessageEvent
from nonebot.matcher import Matcher
from . import _lang
from . import _error
import json

require("nonebot_plugin_apscheduler")

# [HELPSTART] Version: 2
# Command: mcver
# Info: 获取当前最新 Minecraft 版本
# Msg: 获取MC版本
# Usage: mcver
# Command: mcupdate
# Msg: MC更新推送
# Usage: mcupdate
# [HELPEND]


@on_command("mcver").handle()
async def get_minecraft_latest_version(matcher: Matcher, event: Event):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "http://launchermeta.mojang.com/mc/game/version_manifest.json")
        mc_version_data = json.loads(response.read())
        await matcher.finish(_lang.text(
            "mcver.mcver", list(
                mc_version_data["latest"].values()), event.get_user_id()))
    except BaseException:
        await _error.report(traceback.format_exc(), matcher)


@on_command("mcupdate").handle()
async def mcupdate(matcher: Matcher, event: GroupMessageEvent):
    try:
        data = json.load(open("data/mcver.mc_update_notice.enabled.json",
                              encoding="utf-8"))
        if event.group_id not in data:
            data.append(event.group_id)
        else:
            data.pop(data.index(event.group_id))
        json.dump(data, open("data/mcver.mc_update_notice.enabled.json",
                             "w", encoding="utf-8"))
        await matcher.finish(_lang.text(
            f"mcver.{'enabled' if event.group_id in data else 'disabled'}",
            [], event.get_user_id()))
    except BaseException:
        await _error.report(traceback.format_exc(), matcher)


@scheduler.scheduled_job("cron", hour="*/1", id="get_latest_minecraft_version")
async def get_latest_minecraft_version():
    try:
        with open("data/mcver.mc_cache_version.txt", encoding="utf-8") as f:
            mc_cached_version = f.read()
        async with httpx.AsyncClient() as client:
            response = await client.get("http://launchermeta.mojang.com/mc/game/version_manifest.json")
        mc_version_data = json.loads(response.read())
        if mc_version_data["versions"][0]["id"] != mc_cached_version:
            groups = json.load(
                open("data/mcver.mc_update_notice.enabled.json", encoding="utf-8"))
            version = mc_version_data["versions"][0]
            multiAccoutData = json.load(
                open("data/su.multiaccoutdata.ro.json"))
            for group in groups:
                try:
                    await get_bot(multiAccoutData[str(group)]).call_api(
                        "send_group_msg",
                        group_id=group,
                        message=f'发现MC更新：{version["id"]} ({version["type"]})\n{version["time"]}'
                    )
                except BaseException:
                    await _error.report(traceback.format_exc())
            with open("data/mcver.mc_cache_version.txt", "w", encoding="utf-8") as f:
                f.write(version["id"])
    except BaseException:
        await _error.report(traceback.format_exc())
