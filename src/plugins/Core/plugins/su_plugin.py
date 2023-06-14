from nonebot.params import CommandArg
from .su import su
from . import _error
import traceback
import json
from nonebot.adapters import Message


@su.handle()
async def su_plugin(message: Message = CommandArg()):
    try:
        argument = str(message).split(" ")
        if argument[0] in ["plugins", "插件管理", "plugin"]:
            config = json.load(
                open(
                    "data/init.disabled.json",
                    encoding="utf-8"))
            if argument[1] == "disable" or argument[1] == "禁用":
                if argument[2] not in config:
                    config += [argument[2]]
                    await su.send("完成")
            elif argument[1] == "enable" or argument[1] == "启用":
                length = 0
                for conf in config:
                    if conf == argument[2]:
                        config.pop(length)
                        break
                    await su.send("完成")
            json.dump(
                config,
                open(
                    "data/init.disabled.json",
                    "w",
                    encoding="utf-8"))
    except BaseException:
        await _error.report(traceback.format_exc(), su)
