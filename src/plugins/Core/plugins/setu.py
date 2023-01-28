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
latest_ext = ""
config = json.load(open("data/setu.config.json"))
allow_r18 = json.load(open("data/setu.allow.json"))["r18"]


@app.get("/setu", response_class=FileResponse)
async def get_latest_image() -> bytes | str:
    try:
        with open(f"data/setu.image.{latest_ext}", "rb") as f:
            image = f.read()
        return image
    except FileNotFoundError:
        return "错误：未找到图片缓存"


async def delete_msg(bot: Bot, message: int) -> None:
    try:
        await asyncio.sleep(config["delete_sleep"])
        await bot.delete_msg(message_id=message)
    except Exception:
        await _error.report(traceback.format_exc())


@setu.handle()
async def setu_handler(bot: Bot, event: MessageEvent, message: Message = CommandArg()) -> None:
    global latest_send, latest_ext
    try:
        # 冷却
        if time.time() - latest_send <= config["sleep"]:
            await setu.finish(f"冷却中，剩余{config['sleep'] - (time.time() - latest_send)}s")
        await setu.send("少女祈祷中 ...")

        # 收集信息
        argument = message.extract_plain_text().split(" ")
        r18 = 0
        tags = ""
        for argv in argument:
            if argv == "r18":
                if allow_r18:
                    r18 = 1
                else:
                    await setu.finish("R18图片被超管标记为：不允许\n如果需要，请给XDbot2捐一个帐号(x)")
            else:
                tags += f"&tag={argv}"

        # 发起请求
        async with httpx.AsyncClient() as client:
            req = await client.get(f"https://api.lolicon.app/setu/v2?r18={r18}{tags}")
            data = json.loads(req.read())
        if data["error"]:
            await setu.send(f"API发生错误：{data['error']}")

        # 分析数据
        try:
            data = data['data'][0]
        except IndexError:
            await setu.finish("错误：查找失败！（本次不计入冷却）", at_sender=True)
        img_url = data['urls']['original']

        # 下载图片
        async with httpx.AsyncClient(proxies=config["proxies"]) as client:
            req = await client.get(img_url)
            with open(f"data/setu.image.{data['ext']}", "wb") as f:
                f.write(req.read())
        latest_ext = data["ext"]
        image_path = os.path.abspath(f"data/setu.image.{data['ext']}")

        # 生成文本
        msg = MessageSegment.image(f"file://{image_path}")
        msg += data["title"]
        msg += f' (P{data["pid"]})'
        msg += f"\n作者：{data['author']}"
        msg += f"\n[消息将在{config['delete_sleep']}s后撤回]"
        msg = Message(msg)
        # pid = copy.deepcopy(data["pid"])

        # 发送文本
        try:
            try:
                message_id = (
                    await bot.send_group_msg(
                        group_id=int(event.get_session_id().split("_")[1]),
                        message=msg))["message_id"]
            except IndexError:
                message_id = (
                    await bot.send_private_msg(
                        user_id=int(event.get_user_id()),
                        message=msg))["message_id"]
        except ActionFailed:
            await setu.finish((
                f"错误：图片发送失败！（本次不计入冷却）\n"
                f"https://xdbot2.thisisxd.top/setu"))

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
        await _error.report("警告：一个请求超时！")
        await setu.finish("错误：请求超时，请稍候重试！（本次不计入冷却）")
    except FinishedException:
        raise FinishedException()
    except Exception:
        await _error.report(traceback.format_exc(), setu)

# [HELPSTART] Version: 2
# Command: st-r
# Info: 随机图片（增强）
# Usage: st-r [r18] [tag ...]
# [HELPEND]
