from nonebot.params import CommandArg
from .su import su
import traceback
import os
from . import _error
import json


@su.handle()
async def ct(argument: list = str(CommandArg()).split(" ")):
    try:
        if argument[0] == "ct" or argument[0] == "发言排名":
            if argument[1] == "clear" or argument[1] == "清除数据":
                fileList = os.listdir("data")
                for file in fileList:
                    if file.startswith("ct."):
                        json.dump(
                            dict(),
                            open(
                                f"data/{file}",
                                "w",
                                encoding="utf-8"))
                        await su.send(f"已重置：{file}")
                await su.finish("已清除所有发言排名数据")
    except BaseException:
        await _error.report(traceback.format_exc(), su)
