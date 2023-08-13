import json
import re
import traceback
from . import _error
from . import _lang
from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, Message, MessageEvent
from nonebot.exception import FinishedException
from nonebot.params import CommandArg
import os.path
import time
import sys

sys.path.append(os.path.abspath("src/plugins/Core/lib/md2img"))
markdown2image = __import__("markdown2image")
md2img = on_command("md2img", aliases={"markdown渲染", "md渲染"})


@md2img.handle()
async def md2imgHandle(bot: Bot, event: MessageEvent, message: Message = CommandArg()):
    try:
        markdown = message.extract_plain_text()
        # 发送
        filename = f"data/md2img.cache_{time.time()}.ro.png"
        markdown2image.md2img(markdown, filename)
        await md2img.send(
            Message(f"[CQ:image,file=file://{os.path.abspath(filename)}]")
        )
        os.remove(filename)

    except FinishedException:
        raise FinishedException()
    except Exception:
        await _error.report(traceback.format_exc())


# [HELPSTART] Version: 2
# Command: md2img
# Usage: md2img <内容>
# Info: Markdown转图片（还在测试中，如果部分控件没有渲染或渲染不正确就是没写完）
# Msg: MD转图片
# [HELPEND]
