#!/usr/bin/env python
# -*- coding: utf-8 -*-

import asyncio
import json
import random
import re
import time
import traceback
from . import _error
from . import _lang
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
dictionary = {
    "poke": [
        "?",
        "¿",
        "喵？",
        "a？",
        "啊咧？",
        "撒？",
        "哈？",
        "哎呦你干嘛（？",
        "（被撅）哼哼哼啊啊啊啊啊啊啊啊",
        "（拍桌）你是不是有病啊？",
        "（脸红）啊……不可以"
    ],
    "to_me": [
        "?",
        "¿",
        "喵？",
        "a？",
        "（窥屏.jpg）",
        "喵喵喵？"
    ],
    "primary": [
        "（窥屏.jpg）",
        "az……"
    ],
    "tips": [
        "你知道吗：XDbot的生日是2022/06/28",
        "你知道吗：不你不知道",
        "你知道吗：想不出来了如果可以的话给个issue帮着写点把qaq（https://github.com/This-is-XiaoDeng/XDbot2"
    ]
}


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
        await _error.report(traceback.format_exc())


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
                if random.random() <= 0.10:     # 清理图库，机率：5% x 5%
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
        await _error.report(traceback.format_exc())


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
                            f"{_lang.text('reply.pass',[imageID])}"
                            f"{_lang.text('reply.rm',[imageID])}"
                            f"{event.get_session_id()}")),
                        group_id=ctrlGroup
                    )

                    json.dump(data, open("data/reply.images.json", "w"))
                    await asyncio.sleep(random.random() / 2)
                    await imageSaver.send(_lang.text("reply.good_image", [], event.get_user_id()))
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
                            f"{_lang.text('reply.pass',[imageID])}"
                            f"{_lang.text('reply.rm',[imageID])}"
                            f"{event.get_session_id()}")),
                        group_id=ctrlGroup
                    )
                    await asyncio.sleep(random.random() / 2)
                    await imageSaver.send(_lang.text("reply.good_image", [], event.get_user_id()))

                    json.dump(data, open("data/reply.images.json", "w"))
                    latestSend = time.time()
                # elif random.random() <= 0.01:

    except Exception:
        await _error.report(traceback.format_exc())
