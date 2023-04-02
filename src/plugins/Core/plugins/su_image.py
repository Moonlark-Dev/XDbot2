from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Message
from .su import su
from . import _error
import json
import traceback
from nonebot.adapters.onebot.v11 import Message


@su.handle()
async def img_review(message: Message = CommandArg()):
    argument = str(message).split(" ")
    try:
        if argument[0] in ["img", "图库"]:
            data = json.load(open("data/reply.images.json", encoding="utf-8"))
            if argument[1] in ["review", "审核库", "re"]:
                if argument[2] in ["list", "列表"]:
                    for key in data["review"].keys():
                        await su.send(Message(f"「ID：{key}」\n{data['review'][key]}"))
                elif argument[2] in ["pass", "通过"]:
                    if argument[3] in ["all", "所有", "*"]:
                        for key in list(data["review"].keys()):
                            data["B"].append(data["review"].pop(key))
                    else:
                        if len(argument) >= 5:
                            group = argument[4]
                        else:
                            group = "B"
                        tempID = len(data[group])
                        image = data["review"].pop(argument[3])
                        data[group].append(image)
                        await su.send(Message(f"「图片已添加」\n临时ID：{group}{tempID}"))
                elif argument[2] in ["remove", "删除", "rm"]:
                    if argument[3] in ["all", "所有", "*"]:
                        data["review"] = dict()
                    else:
                        data["review"].pop(argument[3])
            json.dump(data, open("data/reply.images.json", "w", encoding="utf-8"))
    except BaseException:
        await _error.report(traceback.format_exc(), su)


@su.handle()
async def image(message: Message = CommandArg()):
    argument = str(message).split(" ")
    try:
        if argument[0] in ["img", "图库"] and argument[1] not in ["review", "re", "审核库"]:
            data = json.load(open("data/reply.images.json", encoding="utf-8"))
            if argument[1] in ["添加", "add"]:
                data[argument[2]].append(argument[3])
            elif argument[1] in ["list", "列表"]:
                length = 0
                for image in data[argument[2]]:
                    await su.send(Message(f"「临时ID：{argument[2]}{length}」\n{image}"))
                    length += 1
            elif argument[1] in ["remove", "删除"]:
                data[argument[2]].pop(int(argument[3]))
            elif argument[1] in ["clear", "清空"]:
                data = {"A": [], "B": [], "C": [], "review": dict()}
            json.dump(data, open("data/reply.images.json", "w", encoding="utf-8"))
    except BaseException:
        await _error.report(traceback.format_exc(), su)
