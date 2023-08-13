#!/usr/bin/env python
# -*- coding: utf-8 -*-

import asyncio
import json
import random
import re
import time
import traceback
from nonebot.exception import FinishedException
from . import _error
from . import _lang
from nonebot import on_message, on_type
from nonebot.rule import to_me
from nonebot.adapters.onebot.v11.event import PokeNotifyEvent
from nonebot.adapters.onebot.v11 import Message
# from nonebot.adapters.onebot.v11.bot import Bot
from nonebot.adapters.onebot.v11.event import GroupMessageEvent

ctrlGroup = json.load(open("data/ctrl.json", encoding="utf-8"))["control"]
repetition = on_message()
send_tips = on_message()
on_poke = on_type(PokeNotifyEvent, rule=to_me())
repetitionCache = dict()
imageSaver = on_message()
imageSender = on_message()
latestSend = time.time()
# on_tome_msg = on_message(rule=to_me())
random_send = on_message()
dictionary = {
    "poke": [
        "?", "¿", "喵？", "a？", "啊咧？", "撒？", "哈？", "哎呦你干嘛（？",
        "（被撅力）哼哼哼啊啊啊啊啊啊啊啊（悲", "（拍桌）你是不是有病啊？", "（脸红）啊……不可以", "杰哥不要！（？"
    ],
    "to_me": ["?", "¿", "喵？", "a？", "喵喵喵？", "(?"],
    "primary": ["az……", "hmm"],
    "tips": [
        "XDbot的生日是2022/06/28！", "你知道吗：不你不知道",
        "XDbot2 是一个开源项目，可以在 https://github.com/ITCraftDevelopmentTeam/XDbot2 上查看 XDbot2 的源代码",
        "以使用「/upload-log」查看当日 XDbot2 运行日志（虽然没有什么用）",
        "XDbot提供了多种风格的语言包，使用「/lang list」可以查看它们", "404 not found", "这里没有tips",
        "现在是 XDbot Version 2", "print('Hello, XDbot2!')", "also try Sugar",
        "怒艹大伟哥出奇迹!", "Let's!Get!!Higher!!!", "Clap!",
        "You know what you know.",
        "You know how you know why you know what you know.", "欢迎回到地球"
    ]
}


@send_tips.handle()
async def send_tips_handle():
    try:
        global latestSend
        if time.time() - latestSend >= 180:
            if random.random() <= 0.015:
                if time.localtime().tm_wday == 3 and random.random() <= 0.1:
                    await send_tips.send("【XDbot小贴士】\n肯德基疯狂星期四，V我50")

                await send_tips.send(
                    f"【XDbot小贴士】\n{random.choice(dictionary['tips'])}")
                latestSend = time.time()
    except FinishedException:
        raise FinishedException()
    except BaseException:
        await _error.report(traceback.format_exc())


@random_send.handle()
async def random_send_handle():
    try:
        global latestSend
        if time.time() - latestSend >= 600:
            if random.random() <= 0.15:
                await random_send.send(random.choice(dictionary["primary"]))
                latestSend = time.time()
    except BaseException:
        await _error.report(traceback.format_exc())


"""
# 由于 gpt 插件，本函数已被暂时弃用
# @on_tome_msg.handle()
async def to_me_msg_handle():
    try:
        if random.random() <= 0.75:
            # 使用 finish 可能会影响 XDbot 继续处理
            await on_tome_msg.send(random.choice(dictionary["to_me"]))
    except BaseException:
        await _error.report(traceback.format_exc())
"""


@on_poke.handle()
async def poke_handle():
    try:
        if random.random() <= 0.75:
            await on_poke.finish(random.choice(dictionary["poke"]))
    except FinishedException:
        raise FinishedException()
    except BaseException:
        await _error.report(traceback.format_exc())


@repetition.handle()
async def repetitionHandle(event: GroupMessageEvent):
    try:
        global latestSend
        # 检查冷却
        if time.time() - latestSend < 15:
            return None
        # 处理信息
        if event.group_id not in repetitionCache.keys():
            repetitionCache[event.group_id] = {
                "message": event.get_plaintext(),
                "user": [event.get_user_id()],
            }
        else:
            if event.get_user_id() not in repetitionCache[
                    event.group_id]["user"]:
                if event.get_plaintext() == repetitionCache[
                        event.group_id]["message"]:
                    repetitionCache[event.group_id]["user"].append(
                        event.get_user_id())
                    if len(repetitionCache[event.group_id]
                           ["user"]) >= random.randint(2, 5):
                        if (len(repetitionCache[event.group_id]["user"])
                                <= random.randint(0, 50) or len(
                                    repetitionCache[event.group_id]["message"])
                                <= 10):
                            await asyncio.sleep(random.random() * 0.3 * (len(
                                repetitionCache[event.group_id]["message"]) /
                                                                         2))
                            await repetition.send(
                                repetitionCache.pop(event.group_id)["message"])
                            latestSend = time.time()
                else:
                    try:
                        repetitionCache.pop(event.group_id)
                    except BaseException:
                        pass

    except Exception:
        await _error.report(traceback.format_exc())


@imageSender.handle()
async def imageSenderHandle(event: GroupMessageEvent):
    try:
        global latestSend
        if time.time() - latestSend > 90:
            if event.group_id in json.load(
                    open("data/random_events.disable.json",
                         encoding="utf-8"))["send_images"]:
                await imageSender.finish()
            if random.random() <= 0.05:  # 机率：5%
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
                if random.random() <= 0.05:
                    images += list(imageData["review"].values())

                images.sort()
                # 发送图片
                image = random.choice(images)
                await asyncio.sleep(random.random() / 2)
                try:
                    await imageSender.send(Message(f"[CQ:image,file={image}]"))
                    latestSend = time.time()
                except BaseException:
                    pass
                if random.random() <= 0.10:  # 清理图库，机率：5% x 5%
                    imageData = json.load(
                        open("data/reply.images.json", encoding="utf-8"))
                    try:
                        b2cLen = random.randint(0, len(imageData["B"]) - 1)
                        removeLen = random.randint(0, len(imageData["C"]) - 1)
                        imageData["C"].append(imageData["B"].pop(b2cLen))
                        if random.random() <= 0.25:
                            imageData["C"].pop(removeLen)
                    except BaseException:
                        pass
                    json.dump(
                        imageData,
                        open("data/reply.images.json", "w", encoding="utf-8"))

    except IndexError:
        pass
    except FinishedException:
        raise FinishedException()
    except Exception:
        await _error.report(traceback.format_exc())


@imageSaver.handle()
async def imageSaverHandle(event: GroupMessageEvent):
    try:
        global latestSend
        if time.time() - latestSend > 60:
            if event.group_id in json.load(
                    open("data/random_events.disable.json",
                         encoding="utf-8"))["download_images"]:
                await imageSaver.finish()
            message = str(event.get_message())
            # await imageSaver.send(message)
            imageCQ = re.match(r"\[CQ:image(.*)\]", message)
            if imageCQ is not None:
                imageCQ = imageCQ.group(0)
                isMeme = int(
                    re.search(r"subType=\d", imageCQ).group(0).split("=")[1])
                # await imageSaver.send(str(bool(isMeme)))
                if isMeme and random.random() <= 0.15:  # 概率：5%
                    data = json.load(
                        open("data/reply.images.json", encoding="utf-8"))
                    imageID = len(data["review"].keys())
                    data["review"][imageID] = imageCQ.split(
                        "url=")[-1].replace("]", "")
                    await _error.report(
                        (f"{imageCQ}\n"
                         f"{_lang.text('reply.pass',[imageID])}"
                         f"{_lang.text('reply.rm',[imageID])}"
                         f"{event.get_session_id()}"))
                    json.dump(
                        data,
                        open("data/reply.images.json", "w", encoding="utf-8"))
                    await asyncio.sleep(random.random())
                    await imageSaver.send(
                        _lang.text("reply.good_image", [],
                                   event.get_user_id()))
                    latestSend = time.time()
                """elif isMeme and random.random() <= 0.10:  # 概率：10%
                    data = json.load(
                        open(
                            "data/reply.images.json",
                            encoding="utf-8"))
                    imageID = len(data["review"].keys())
                    data["review"][imageID] = imageCQ
                    await bot.send_group_msg(
                        message=Message(
                            (
                                f"{imageCQ}\n"
                                f"{_lang.text('reply.pass',[imageID])}"
                                f"{_lang.text('reply.rm',[imageID])}"
                                f"{event.get_session_id()}"
                            )
                        ),
                        group_id=ctrlGroup,
                    )
                    await asyncio.sleep(random.random() / 2)
                    await imageSaver.send(
                        _lang.text("reply.good_image", [], event.get_user_id())
                    )

                    json.dump(
                        data,
                        open(
                            "data/reply.images.json",
                            "w",
                            encoding="utf-8"))
                    latestSend = time.time()
                # elif random.random() <= 0.01:"""

    except Exception:
        await _error.report(traceback.format_exc())
