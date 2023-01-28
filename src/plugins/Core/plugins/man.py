import json
import re
import traceback
from . import _error
from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, Message
from nonebot.exception import FinishedException
from nonebot.params import CommandArg

man = on_command("man", aliases={"手册", "info"})
ctrlGroup = json.load(open("data/ctrl.json", encoding="utf-8"))["control"]


@man.handle()
async def manHandle(
        bot: Bot,
        message: Message = CommandArg()):
    try:
        argument = message.extract_plain_text()
        if argument == "":
            with open("docs/README.md", encoding="utf-8") as f:
                text = f.read()
            # 去换行
            while True:
                if text[-1] == "\n":
                    text = text[:-1]
                else:
                    break
            # 发送
            await man.finish(
                text.replace("\n", " \n")
                    .replace("#", "  ")
                    .replace("`", " ")
                    .replace(">", "  ")
            )
        else:
            command = re.search(r"[A-Za-z]+", argument)
            page = re.search(r"[0-9]+", argument) or "0"
            if command:
                command = command.group(0)
            if page and not isinstance(page, str):
                page = page.group(0)
            # 读取文件
            with open(f"docs/{command}/{page}.md", encoding="utf-8") as f:
                text = f.read()
            # 去末尾换行
            while True:
                if text[-1] == "\n":
                    text = text[:-1]
                else:
                    break
            # 发送
            await man.finish(
                text.replace("\n", " \n")
                    .replace("#", " ")
                    .replace("`", " ")
            )

    except FinishedException:
        raise FinishedException()
    except FileNotFoundError:
        await man.finish("手……手册找不到， 哼哼哼啊啊啊啊啊啊")
    except Exception:
        await _error.report(traceback.format_exc(), man)

# [HELPSTART] Version: 2
# Command: man
# Usage man [章节] [页面]：查看手册指定章节
# Info XDbot2 内置的使用参考手册
# Msg: XDbot2 使用手册
# [HELPEND]
