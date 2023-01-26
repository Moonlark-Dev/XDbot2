#!/usr/bin/env python
# -*- coding: utf-8 -*-

from nonebot import on_command
from nonebot.adapters.onebot.v11.message import MessageSegment
from nonebot.adapters.onebot.v11.bot import Bot
from nonebot.adapters.onebot.v11 import Message
from nonebot.adapters.onebot.v11.event import MessageEvent
from nonebot.exception import FinishedException, ActionFailed
from nonebot.params import CommandArg
from . import _error
import asyncio
import traceback
import httpx
import json
import os.path
import time

setu = on_command("setu", aliases={"涩图", "st-r"})
latest_send = time.time()
config = json.load(open("data/setu.config.json"))


async def delete_msg(bot: Bot, message: int) -> None:
    try:
        await asyncio.sleep(config["delete_sleep"])
        await bot.delete_msg(message_id=message)
    except Exception:
        await _error.report(traceback.format_exc())


@setu.handle()
async def setu_handler(bot: Bot, event: MessageEvent, message: Message = CommandArg()) -> None:
    global latest_send
    try:
        # 冷却
        if time.time() - latest_send <= config["sleep"]:
            await setu.finish(f"冷却中，剩余{config['sleep'] - (time.time() - latest_send)}s")
        
        # 收集信息
        argument = message.extract_plain_text().split(" ")
        r18 = 0
        tags = ""
        for argv in argument:
            if argv == "r18":
                r18 = 1
            else:
                tags += f"&tag={argv}"
        
        # 发起请求
        async with httpx.AsyncClient() as client:
            req = await client.get(f"https://api.lolicon.app/setu/v2?r18={r18}{tags}")
            data = json.loads(req.read())
        if data["error"]:
            await setu.send(f"API发生错误：{data['error']}")

        # 分析数据
        data = data['data'][0]
        img_url = data['urls']['original']

        # 下载图片
        async with httpx.AsyncClient(proxies=config["proxies"]) as client:
            req = await client.get(img_url)
            with open(f"data/setu.image.{data['ext']}", "wb") as f:
                f.write(req.read())
        image_path = os.path.abspath(f"data/setu.image.{data['ext']}")

        # 生成文本
        msg = MessageSegment.image(f"file://{image_path}")
        msg += data["title"]
        msg += f' (P{data["pid"]})'
        msg += f"\n作者：{data['author']}"
        msg += f"\n[消息将在{config['delete_sleep']}s后撤回]"
        msg = Message(msg)

        # 发送文本
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

        # 启动删除任务
        asyncio.create_task(delete_msg(bot, message_id))
        latest_send = time.time()

    except httpx.ConnectTimeout:
        await _error.report("警告：一个请求超时！")
        await setu.finish("错误：请求超时，请稍候重试！（本次不计入冷却）")
    except ActionFailed:
        await setu.finish("错误：图片被腾讯风控！（本次不计入冷却）")
    except FinishedException:
        raise FinishedException()
    except Exception:
        await _error.report(traceback.format_exc(), setu)
