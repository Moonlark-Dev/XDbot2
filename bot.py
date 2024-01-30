#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import nonebot
from nonebot.adapters.onebot.v11 import Adapter as ONEBOT_V11Adapter
from nonebot.log import logger, default_format
import os

try:
    os.mkdir("data")
except Exception:
    pass
os.system("git submodule update")

logger.add(
    "./data/error.log",
    rotation="00:00",
    diagnose=False,
    level="WARNING",
    format=default_format,
)

nonebot.init()
app = nonebot.get_asgi()
driver = nonebot.get_driver()
driver.register_adapter(ONEBOT_V11Adapter)
nonebot.load_from_toml("pyproject.toml")

if __name__ == "__main__":
    nonebot.logger.warning(
        "Always use `nb run` to start the bot instead of manually running!"
    )
    nonebot.run(app="__mp_main__:app")
