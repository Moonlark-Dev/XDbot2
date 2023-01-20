#!/usr/bin/env python
# -*- coding: utf-8 -*-

import asyncio
import json
import random
import re
import time
import traceback

from nonebot import on_message
from nonebot.adapters.onebot.v11 import Message
from nonebot.adapters.onebot.v11.bot import Bot
from nonebot.adapters.onebot.v11.event import GroupMessageEvent

ctrlGroup = json.load(open("data/ctrl.json", encoding="utf-8"))["control"]
repetition = on_message()
repetitionCache = dict()
imageSaver = on_message()
imageSender = on_message()
latestSend = time.time()


@repetition.handle()
async def repetitionHandle(
        bot: Bot,
        event: GroupMessageEvent):
    try:
        global latestSend
        # 检查冷却
        if time.time() - latestSend < 15:
            return None
        # 处理信息
        if event.group_id not in repetitionCache.keys():
            repetitionCache[event.group_id] = {
                "message": event.get_plaintext(),
                "user": [event.get_user_id()]
            }
        else:
            if event.get_user_id(
            ) not in repetitionCache[event.group_id]["user"]:
                if event.get_plaintext(
                ) == repetitionCache[event.group_id]["message"]:
                    repetitionCache[event.group_id]["user"].append(
                        event.get_user_id())
                    if len(repetitionCache[event.group_id]
                           ["user"]) >= random.randint(2, 5):
                        if (len(repetitionCache[event.group_id]["user"]) <= random.randint(0, 50)
                                or len(repetitionCache[event.group_id]["message"]) <= 10):
                            await asyncio.sleep(random.random() * 0.3 * (len(repetitionCache[event.group_id]["message"]) / 2))
                            await repetition.send(repetitionCache[event.group_id]["message"])
                            repetitionCache.pop(event.group_id)
                            latestSend = time.time()
                else:
                    try:
                        repetitionCache.pop(event.group_id)
                    except BaseException:
                        pass

    except Exception:
        await bot.send_group_msg(
            message=traceback.format_exc(),
            group_id=ctrlGroup
        )


@imageSender.handle()
async def imageSenderHandle(bot: Bot):
    try:
        global latestSend
        if time.time() - latestSend > 90:
            if random.random() <= 0.05:     # 机率：5%
                images = []
                # message = event.get_plaintext()
                imageData = json.load(
                    open("data/reply.images.json", encoding="utf-8"))
                # 初始化图库
                for image in imageData["A"]:
                    images += [image, image, image]
                for image in imageData["B"]:
                    images += [image, image]
                for image in imageData["C"]:
                    images += [image]

                images.sort()
                # 发送图片
                image = random.choice(images)
                await asyncio.sleep(random.random() / 2)
                await imageSender.send(Message(image))
                latestSend = time.time()
            if random.random() <= 0.15:     # 清理图库，机率：15%
                imageData = json.load(
                    open("data/reply.images.json", encoding="utf-8"))
                try:
                    b2cLen = random.randint(0, len(imageData["B"]) - 1)
                    removeLen = random.randint(0, len(imageData["C"]) - 1)
                    imageData["C"].append(imageData["B"].pop(b2cLen))
                    imageData["C"].pop(removeLen)
                except BaseException:
                    pass
                json.dump(imageData, open(
                    "data/reply.images.json", "w", encoding="utf-8"))

    except Exception:
        await bot.send_group_msg(
            message=traceback.format_exc(),
            group_id=ctrlGroup
        )


@imageSaver.handle()
async def imageSaverHandle(
        bot: Bot,
        event: GroupMessageEvent):
    try:
        global latestSend
        if time.time() - latestSend > 60:
            message = str(event.get_message())
            # await imageSaver.send(message)
            imageCQ = re.match(r"\[CQ:image(.*)\]", message)
            if imageCQ is not None:
                imageCQ = imageCQ.group(0)
                isMeme = int(
                    re.search(
                        r"subType=\d",
                        imageCQ).group(0).split("=")[1])
                # await imageSaver.send(str(bool(isMeme)))
                if isMeme and random.random() <= 0.05:      # 概率：5%
                    data = json.load(
                        open(
                            "data/reply.images.json",
                            encoding="utf-8"))
                    imageID = len(data["review"].keys())
                    data["review"][imageID] = imageCQ
                    await bot.send_group_msg(
                        message=Message((
                            f"{imageCQ}\n"
                            f"使用 /su img re pass {imageID} [组] 通过\n"
                            f"使用 /su img re rm {imageID} 删除\n"
                            f"{event.get_session_id()}")),
                        group_id=ctrlGroup
                    )

                    json.dump(data, open("data/reply.images.json", "w"))
                    await asyncio.sleep(random.random() / 2)
                    await imageSaver.send("好图，我的了")
                    latestSend = time.time()
                elif isMeme and random.random() <= 0.10:      # 概率：10%
                    data = json.load(
                        open(
                            "data/reply.images.json",
                            encoding="utf-8"))
                    imageID = len(data["review"].keys())
                    data["review"][imageID] = imageCQ
                    await bot.send_group_msg(
                        message=Message((
                            f"{imageCQ}\n"
                            f"使用 /su img re pass {imageID} [组] 通过\n"
                            f"使用 /su img re rm {imageID} 删除\n"
                            f"{event.get_session_id()}")),
                        group_id=ctrlGroup
                    )
                    await asyncio.sleep(random.random() / 2)
                    await imageSaver.send("好图，我的了")

                    json.dump(data, open("data/reply.images.json", "w"))
                    latestSend = time.time()
                # elif random.random() <= 0.01:

    except Exception:
        await bot.send_group_msg(
            message=traceback.format_exc(),
            group_id=ctrlGroup
        )
