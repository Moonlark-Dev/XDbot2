from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Message
from .su import su
from . import _error
import json
import traceback


@su.handle()
async def set_config(message: Message = CommandArg()):
    argument = str(message).split(" ")
    try:
        if argument[0] in ["config", "配置"]:
            if argument[1] in ["set-key", "设置键"]:
                config = json.load(
                    open(f"data/{argument[2]}", encoding="utf-8"))
                config[json.loads(argument[3])] = " ".join(argument[4:])
                json.dump(config, open(
                    f"data/{argument[2]}", "w", encoding="utf-8"))

                await su.finish(f"{argument[2]}::{argument[3]} -> {' '.join(argument[4:])}")
            elif argument[0] in ["set", "设置"]:
                with open(f"data/{argument[2]}", "w", encoding="utf-8") as f:
                    f.write(" ".join(argument[3:]))
                await su.finish(f"{argument[2]} -> {' '.join(argument[3:])}")
    except BaseException:
        await _error.report(traceback.format_exc(), su)


@su.handle()
async def get_config(message: Message = CommandArg()):
    argument = str(message).split(" ")
    try:
        if argument[0] in ["config", "配置"]:
            if argument[1] in ["get", "获取"]:
                if len(argument) >= 4:
                    await su.finish(str(
                        json.dumps(
                            json.load(open(f"data/{argument[2]}", encoding="utf-8"))[
                                json.loads(" ".join(argument[3:]))
                            ]
                        )
                    ))
                else:
                    with open(f"data/{argument[2]}", encoding="utf-8") as f:
                        await su.finish(f.read())
    except BaseException:
        await _error.report(traceback.format_exc(), su)
