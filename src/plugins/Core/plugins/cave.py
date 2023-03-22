import json
import os
import os.path
import random
import time
import traceback
import marshal
import re
from . import _error
from .etm import exp
from . import _lang
import httpx
from nonebot import on_command, get_app, on_message
from nonebot.adapters.onebot.v11 import Bot, Message, MessageEvent
from nonebot.exception import FinishedException
from nonebot.params import CommandArg

cave = on_command("cave", aliases={"回声洞"})
cave_comment = on_message()
ctrlGroup = json.load(open("data/ctrl.json", encoding="utf-8"))["control"]
latest_use = time.time()
path = os.path.abspath(os.path.dirname("."))
app = get_app()
commandHelp = {
    "cave": {
        "name": "cave",
        "info": "随机、投稿或查询 回声洞",
        "msg": "回声洞",
        "usage": [
            "cave：随机一条回声洞",
            "cave-a <内容>：投稿一条回声洞（见cave(1)）",
            "cave-g <回声洞ID>：查看指定回声洞",
            "cave-q <开始ID> <结束ID>：查询一堆范围内的回声洞"
        ],
    }
}
MAX_NODE_MESSAGE = 200


@cave_comment.handle()
async def cave_comment_writer(event: MessageEvent):
    try:
        if not event.reply:
            await cave_comment.finish()
        reply_message = str(event.reply.message)
        if re.match(r"回声洞——（(0|[1-9][0-9]*)）\n(.+)\n——(.*)", reply_message):
            # 懒得写了就这样吧
            cave_id = re.search(
                r"回声洞——（[0-9]+）",
                reply_message)[0].replace(
                "回声洞——（",
                "").replace(
                "）",
                "")
            data = json.load(open("data/cave.comments.json", encoding="utf-8"))
            if cave_id not in data.keys():
                data[cave_id] = {"count": 1, "data": {}}
            data[cave_id]["data"][str(data[cave_id]["count"])] = {
                "id": data[cave_id]["count"],
                "text": str(event.get_message()),
                "sender": event.get_user_id()
            }
            data[cave_id]["count"] += 1
            json.dump(data, open(
                "data/cave.comments.json", "w", encoding="utf-8"))
            await _error.report(f"「新回声洞评论（{cave_id}#{data[cave_id]['count'] - 1}）」\n{event.get_message()}\n{event.get_session_id()}")
            exp.add_exp(event.get_user_id(), 3)
            await cave_comment.finish(f"评论成功：{cave_id}#{data[cave_id]['count'] - 1}")

    except FinishedException:
        raise FinishedException()
    except BaseException:
        await _error.report(traceback.format_exc(), cave_comment)


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
                      4: message.find("]", cqStart)]
        imageID = str(time.time())
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            with open(f"data/caveImages/{imageID}.png", "wb") as f:
                f.write(response.read())
        return await downloadImages(
            message.replace(
                message[cqStart: message.find(
                    "]", cqStart)], f"[[Img:{imageID}]]"
            )
        )


def parseCave(text: str):
    imageIDStart = text.find("[[Img:")
    if imageIDStart == -1:
        return text
    else:
        imageID = text[imageIDStart + 6: text.find("]]]", imageIDStart)]
        imagePath = os.path.join(path, "data", "caveImages", f"{imageID}.png")
        imageCQ = f"[CQ:image,file=file://{imagePath}]"
        return parseCave(text.replace(f"[[Img:{imageID}]]]", str(imageCQ)))


@cave.handle()
async def cave_handle(bot: Bot, event: MessageEvent, message: Message = CommandArg()):
    global latest_use
    try:
        data = json.load(open("data/cave.data.json", encoding="utf-8"))
        argument = str(message).splitlines()
        if len(argument) == 0:
            argument.append("")
        else:
            argument = argument[0].split(" ")
        if argument[0] not in ["add", "添加", "-a"] and time.time() - \
                latest_use < 3:
            await cave.finish(f"冷却中（{3 - (time.time() - latest_use)}s）", at_sender=True)
        else:
            latest_use = time.time()
        if argument[0] == "":
            caveList = data["data"].values()
            random.seed(marshal.loads(b"\xe9" + os.urandom(4)))
            caveData = random.choice(list(caveList))
            text = parseCave(caveData["text"])
            if isinstance(caveData["sender"], dict):
                if caveData["sender"]["type"] == "nickname":
                    senderData = {"nickname": caveData["sender"]["name"]}
                else:
                    senderData = {"nickname": "未知"}
            else:
                senderData = await bot.get_stranger_info(user_id=caveData["sender"])
            await cave.send(
                Message((
                    f'{_lang.text("cave.name",[],event.get_user_id())}——（{caveData["id"]}）\n'
                    f'{text}\n'
                    f"——{senderData['nickname']}")))
            # 发送评论
            if event.get_session_id().split("_")[0] == "group":
                comments = json.load(
                    open("data/cave.comments.json", encoding="utf-8"))
                caveData["id"] = str(caveData["id"])
                if caveData["id"] in comments.keys():
                    comments = list(comments[caveData["id"]]["data"].values())
                    node_message = [[]]
                    count = 0

                    while len(comments) > 0:
                        if count <= MAX_NODE_MESSAGE:
                            comment = comments.pop(-1)
                            node_message[-1].append({
                                "type": "node",
                                "data": {
                                    "uin": comment["sender"],
                                    "nickname": f"来自【{(await bot.get_stranger_info(user_id=comment['sender']))['nickname']}】的评论 - #{comment['id']}",
                                    "content": comment["text"]
                                }
                            })
                        else:
                            node_message.append([])
                            count = 0

                    for node in node_message:
                        await bot.call_api(
                            api="send_group_forward_msg",
                            messages=node,
                            group_id=event.get_session_id().split("_")[1]
                        )
            await cave.finish()

        elif argument[0] in ["query", "-q", "查询"]:
            start_id = int(argument[1])
            end_id = int(argument[2])
            node_message = []
            user_info = await bot.get_login_info()

            keys = data["data"].keys()
            for id in range(start_id, end_id):
                if str(id) in keys:
                    caveData = data["data"][str(id)]

                    text = parseCave(caveData["text"])
                    if isinstance(caveData["sender"], dict):
                        if caveData["sender"]["type"] == "nickname":
                            senderData = {
                                "nickname": caveData["sender"]["name"]}
                        else:
                            senderData = {"nickname": "未知"}
                    else:
                        senderData = await bot.get_stranger_info(user_id=caveData["sender"])
                    cave_text = (
                        f"{_lang.text('cave.name',[],event.get_user_id())}——（{caveData['id']}）\n"
                        f"{text}\n"
                        f"——{senderData['nickname']}\n"
                    )

                    node_message.append({
                        "type": "node",
                        "data": {
                            "uin": int(user_info["user_id"]),
                            "nickname": user_info["nickname"],
                            "content": cave_text
                        }
                    })
            await bot.call_api(
                api="send_group_forward_msg",
                messages=node_message,
                group_id=str(event.get_session_id().split("_")[1])
            )

        elif argument[0] in ["add", "-a", "添加"]:
            exp.add_exp(event.get_user_id(), 6)
            text = await downloadImages(str(message)[argument[0].__len__():].strip())
            data["data"][data["count"]] = {
                "id": data["count"],
                "text": text,
                "sender": event.get_user_id(),
                "time": time.time()
            }
            data["count"] += 1
            # 发送通知
            await bot.send_group_msg(
                message=Message(
                    (
                        f"{_lang.text('cave.new',[data['count']-1])}"
                        f"{event.get_session_id()}\n \n"
                        f"{str(message)[argument[0].__len__():].strip()}"
                    )
                ),
                group_id=ctrlGroup,
            )
            # 写入数据
            json.dump(data, open("data/cave.data.json", "w", encoding="utf-8"))
            await cave.finish(
                _lang.text(
                    "cave.added", [
                        data["count"] - 1], event.get_user_id())
            )

        elif argument[0] in ["-g", "查询", "view", "show", "查看"]:
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
                senderData = await bot.get_stranger_info(user_id=caveData["sender"])
            await cave.send(
                Message(
                    f"""{_lang.text("cave.name",[],event.get_user_id())}——（{caveData['id']}）
{text}
——{senderData['nickname']}"""
                )
            )
            if event.get_session_id().split("_")[0] == "group":
                comments = json.load(
                    open("data/cave.comments.json", encoding="utf-8"))
                caveData["id"] = str(caveData["id"])
                if caveData["id"] in comments.keys():
                    comments = list(comments[caveData["id"]]["data"].values())
                    node_message = [[]]
                    count = 0

                    while len(comments) > 0:
                        if count <= MAX_NODE_MESSAGE:
                            comment = comments.pop(-1)
                            node_message[-1].append({
                                "type": "node",
                                "data": {
                                    "uin": comment["sender"],
                                    "nickname": f"来自【{(await bot.get_stranger_info(user_id=comment['sender']))['nickname']}】的评论 - #{comment['id']}",
                                    "content": comment["text"]
                                }
                            })
                        else:
                            node_message.append([])
                            count = 0

                    for node in node_message:
                        await bot.call_api(
                            api="send_group_forward_msg",
                            messages=node,
                            group_id=event.get_session_id().split("_")[1]
                        )
            await cave.finish()

        elif argument[0] in ["-d", "data", "数据"]:
            await cave.send(_lang.text("cave.data_collecting", [], event.get_user_id()))
            count = data["count"]
            canReadCount = len(data["data"].keys())
            await cave.finish(
                _lang.text(
                    "cave.data_finish", [
                        count, canReadCount], event.get_user_id()
                )
            )

    except FinishedException:
        raise FinishedException()
    except KeyError as e:
        await cave.finish(_lang.text("cave.notfound", [e], event.get_user_id()))
    except Exception:
        await _error.report(traceback.format_exc(), cave)
