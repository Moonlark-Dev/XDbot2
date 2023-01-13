import traceback
import re
import json
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
    except Exception:
        await bot.send_group_msg(
            message=traceback.format_exc(),
            group_id=ctrlGroup)
        await man.finish("处理失败")
