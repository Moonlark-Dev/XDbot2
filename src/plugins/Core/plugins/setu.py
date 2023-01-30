#!/usr/bin/env python
# -*- coding: utf-8 -*-

from nonebot import on_command, get_app
from nonebot.adapters.onebot.v11.message import MessageSegment
from nonebot.adapters.onebot.v11.bot import Bot
from nonebot.adapters.onebot.v11 import Message
from nonebot.adapters.onebot.v11.event import MessageEvent
from nonebot.exception import FinishedException, ActionFailed
from nonebot.params import CommandArg
from . import _error
from . import _lang
from fastapi.responses import FileResponse
import asyncio
import traceback
import httpx
import json
import os.path
import time

# import copy

setu = on_command("setu", aliases={"涩图", "st-r"})
latest_send = time.time()
app = get_app()
image_path = ""
config = json.load(open("data/setu.config.json"))
allow_r18 = json.load(open("data/setu.allow.json"))["r18"]


@app.get("/setu")
async def get_latest_image() -> FileResponse:
    return FileResponse(path=image_path)


async def delete_msg(bot: Bot, message: int) -> None:
    try:
        await asyncio.sleep(config["delete_sleep"])
        await bot.delete_msg(message_id=message)
    except Exception:
        await _error.report(traceback.format_exc())


@setu.handle()
async def setu_handler(
    bot: Bot, event: MessageEvent, message: Message = CommandArg()
) -> None:
    global latest_send, image_path
    try:
        # 冷却
        if time.time() - latest_send <= config["sleep"]:
            await setu.finish(
                _lang.text(
                    "setu.cd",
                    [config["sleep"] - (time.time() - latest_send)],
                    event.get_user_id(),
                )
            )
        await setu.send(_lang.text("setu.cd2", [], event.get_user_id()))

        # 收集信息
        argument = message.extract_plain_text().split(" ")
        r18 = 0
        tags = ""
        for argv in argument:
            if argv == "r18":
                if allow_r18:
                    r18 = 1
                else:
                    await setu.finish(
                        _lang.text("setu.no_r18", [], event.get_user_id())
                    )
            else:
                tags += f"&tag={argv}"

        # 发起请求
        async with httpx.AsyncClient() as client:
            req = await client.get(f"https://api.lolicon.app/setu/v2?r18={r18}{tags}")
            data = json.loads(req.read())
        if data["error"]:
            await setu.send(
                _lang.text(
                    "setu.api_error", [
                        data["error"]], event.get_user_id())
            )

        # 分析数据
        try:
            data = data["data"][0]
        except IndexError:
            await setu.finish(
                _lang.text("setu.index_error", [], event.get_user_id()), at_sender=True
            )
        img_url = data["urls"]["original"]

        # 下载图片
        async with httpx.AsyncClient(proxies=config["proxies"]) as client:
            req = await client.get(img_url)
            with open(f"data/setu.image.{data['ext']}", "wb") as f:
                f.write(req.read())
        image_path = os.path.abspath(f"data/setu.image.{data['ext']}")

        # 生成文本
        msg = MessageSegment.image(f"file://{image_path}")
        msg += data["title"]
        msg += _lang.text("setu.msg1", [data["pid"]], event.get_user_id())
        msg += _lang.text("setu.msg2", [data["author"]], event.get_user_id())
        msg += _lang.text("setu.msg3",
                          [config["delete_sleep"]],
                          event.get_user_id())
        msg = Message(msg)
        # pid = copy.deepcopy(data["pid"])

        # 发送文本
        try:
            try:
                message_id = (
                    await bot.send_group_msg(
                        group_id=int(event.get_session_id().split("_")[1]), message=msg
                    )
                )["message_id"]
            except IndexError:
                message_id = (
                    await bot.send_private_msg(
                        user_id=int(event.get_user_id()), message=msg
                    )
                )["message_id"]
        except ActionFailed:
            await setu.finish(
                (
                    f"{_lang.text('setu.action_failed',[],event.get_user_id())}"
                    f"https://xdbot2.thisisxd.top/setu"
                )
            )

        # 启动删除任务
        asyncio.create_task(delete_msg(bot, message_id))
        latest_send = time.time()

        # 修改调用数据
        data = json.load(open("data/setu.count.json"))
        try:
            data[event.get_user_id()] += 1
        except KeyError:
            data[event.get_user_id()] = 1
        json.dump(data, open("data/setu.count.json", "w"))

    except httpx.ConnectTimeout:
        await _error.report(_lang.text("setu.timeout1"))
        await setu.finish(_lang.text("setu.timeout2", [], event.get_user_id()))
    except FinishedException:
        raise FinishedException()
    except Exception:
        await _error.report(traceback.format_exc(), setu)


# [HELPSTART] Version: 2
# Command: st-r
# Info: 随机图片（增强）
# Usage: st-r [r18] [tag ...]
# [HELPEND]
