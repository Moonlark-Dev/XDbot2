from nonebot.params import CommandArg
from .su import su
from . import _error
import json
import traceback

@su.handle()
async def get_config(argument: list = str(CommandArg()).split(" ")):
    try:
        if argument[0] in ["config", "配置"]:
            if argument[1] == "get" or argument[1] == "获取":
                if len(argument) >= 4:
                    await su.finish(
                        json.dumps(
                            json.load(open(f"data/{argument[2]}", encoding="utf-8"))[
                                " ".join(argument[3:])
                            ]
                        )
                    )
                else:
                    with open(f"data/{argument[2]}", encoding="utf-8") as f:
                        await su.finish(f.read())
    except:
        await _error.report(traceback.format_exc(), su)
