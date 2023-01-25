import json
import os
import os.path
import random
import time
import traceback
import marshal
from . import _error
import httpx
from nonebot import on_command, get_app
from nonebot.adapters.onebot.v11 import (Bot, Message, MessageEvent)
from nonebot.exception import FinishedException
from nonebot.params import CommandArg

cave = on_command("cave", aliases={"回声洞"})
ctrlGroup = json.load(open("data/ctrl.json"))["control"]
path = os.path.abspath(os.path.dirname("."))
app = get_app()
commandHelp = {
    "cave": {
        "name":
        "cave",
        "info":
        "随机、投稿或查询 回声洞",
        "msg":
        "回声洞",
        "usage": [
            "cave：随机一条回声洞", "cave-a <内容>：投稿一条回声洞（见cave(1)）",
            "cave-g <回声洞ID>：查看置顶回声洞"
        ]
    }
}


@app.get("/cave/data.json")
async def getCaveData():
    return json.load(open("data/cave.data.json", encoding="utf-8"))


async def downloadImages(message: str):
    cqStart = message.find("[CQ:image")
    # print("message", message)
    if cqStart == -1:
        return message
    else:
        url = message[message.find("url=", cqStart) +
                      4:message.find("]", cqStart)]
        imageID = str(time.time())
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            with open(f"data/caveImages/{imageID}.png", "wb") as f:
                f.write(response.read())
        return await downloadImages(
            message.replace(message[cqStart:message.find("]", cqStart)],
                            f"[[Img:{imageID}]]"))


def parseCave(text: str):
    imageIDStart = text.find("[[Img:")
    if imageIDStart == -1:
        return text
    else:
        imageID = text[imageIDStart + 6:text.find("]]]", imageIDStart)]
        imagePath = os.path.join(path, "data", "caveImages", f"{imageID}.png")
        imageCQ = f"[CQ:image,file=file://{imagePath}]"
        return parseCave(text.replace(f"[[Img:{imageID}]]]", str(imageCQ)))


@cave.handle()
async def cave_handle(bot: Bot,
                      event: MessageEvent,
                      message: Message = CommandArg()):
    try:
        data = json.load(open("data/cave.data.json", encoding="utf-8"))
        argument = str(message).split(" ")
        if argument[0] == "":
            caveList = data["data"].values()
            random.seed(marshal.loads(b'\xe9' + os.urandom(4)))
            caveData = random.choice(list(caveList))
            text = parseCave(caveData["text"])
            if isinstance(caveData["sender"], dict):
                if caveData["sender"]["type"] == "nickname":
                    senderData = {"nickname": caveData["sender"]["name"]}
                else:
                    senderData = {"nickname": "未知"}
            else:
                senderData = await bot.get_stranger_info(
                    user_id=caveData["sender"])
            await cave.finish(
                Message(f"""回声洞——（{caveData['id']}）
{text}
——{senderData['nickname']}"""))

        elif argument[0] in ["add", "-a", "添加"]:
            text = await downloadImages(
                str(message)[argument[0].__len__():].strip())
            data["data"][data["count"]] = {
                "id": data["count"],
                "text": text,
                "sender": event.get_user_id()
            }
            data["count"] += 1
            # 发送通知
            await bot.send_group_msg(message=Message(
                (f"「回声洞新投稿（{data['count'] - 1}）」\n"
                 f"来自：{event.get_session_id()}\n"
                 f"内容：{str(message)[argument[0].__len__():].strip()}")),
                group_id=ctrlGroup)
            # 写入数据
            json.dump(data, open("data/cave.data.json", "w", encoding="utf-8"))
            await cave.finish(f"回声洞（{data['count'] - 1}）已添加")

        elif argument[0] in ["-g", "查询"]:
            caveData = data["data"][argument[1]]
            text = parseCave(caveData["text"])
            # senderData = await bot.get_stranger_info(user_id=caveData["sender"]
            #                                         )
            if isinstance(caveData["sender"], dict):
                if caveData["sender"]["type"] == "nickname":
                    senderData = {"nickname": caveData["sender"]["name"]}
                else:
                    senderData = {"nickname": "未知"}
            else:
                senderData = await bot.get_stranger_info(
                    user_id=caveData["sender"])
            await cave.finish(
                Message(f"""回声洞——（{caveData['id']}）
{text}
——{senderData['nickname']}"""))
        elif argument[0] in ["-d", "data", "数据"]:
            await cave.send("正在收集数据，请稍候")
            count = data['count']
            canReadCount = len(data['data'].keys())
            await cave.finish(f"总数：{count}\n有效：{canReadCount}")

    except FinishedException:
        raise FinishedException()
    except KeyError as e:
        await cave.finish(f"回声洞（{e}）不存在")
    except Exception:
        await _error.report(traceback.format_exc(), cave)
