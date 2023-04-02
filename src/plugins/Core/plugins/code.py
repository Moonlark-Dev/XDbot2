import traceback
import httpx
from nonebot import on_command
from nonebot.adapters.onebot.v11 import (
    ActionFailed,
    Bot,
    Message,
    GroupMessageEvent,
    PrivateMessageEvent,
)
from nonebot.adapters.onebot.v11.message import MessageSegment
from nonebot.exception import FinishedException
from nonebot.params import CommandArg
import json
from . import _error
from . import _lang
import asyncio

code = on_command("code", aliases={"运行代码"})
header = {
    "Authorization": "Token a238bd14-14ae-43e4-a7ea-8942edd9b98c",
    "Content-Type": "application/json",
}
file_types = {
    "python": ".py",
    "cpp": ".cpp",
    "c": ".c",
    "bash": ".sh",
    "rust": ".rs",
    "java": ".java",
}


async def run_code(message: Message):
    # 收集信息
    arguments = str(message).split("\n")[0].strip().split(" ")
    language = arguments[0]
    if len(arguments) >= 3:
        stdin = arguments[-1].replace("&#91;", "[").replace("&#93;", "]")
    else:
        stdin = ""
    if language in file_types.keys():
        file_type = file_types[language]
    else:
        file_type = ""
    src = (
        "\n".join(str(message).split("\n")[1:])
        .replace("&#91;", "[")
        .replace("&#93;", "]")
    )
    # 请求数据
    request_data = {
        "files": [{"name": f"main{file_type}", "content": src}],
        "stdin": stdin,
    }
    # 发送请求
    async with httpx.AsyncClient() as client:
        response = await client.post(
            url=f"https://glot.io/api/run/{language}/latest",
            headers=header,
            data=json.dumps(request_data),
        )
    data = json.loads(response.read())
    # 分析数据
    if "message" in data.keys():
        return data["message"]
    elif data["stderr"]:
        return data["stderr"]
    elif data["error"]:
        return data["error"]
    else:
        return data["stdout"]


@code.handle()
async def code_handler(
    bot: Bot, event: GroupMessageEvent, message: Message = CommandArg()
):
    try:
        try:
            message_id = (
                await bot.send_group_msg(
                    message=await run_code(message),
                    group_id=event.group_id,
                    auto_escape=True,
                )
            )["message_id"]

        except ActionFailed:
            await code.finish(_lang.text("code.too_long", [], str(event.user_id)))
        await asyncio.sleep(60)
        await bot.delete_msg(message_id=message_id)
    except FinishedException:
        raise FinishedException()
    except BaseException:
        await _error.report(traceback.format_exc(), code)


@code.handle()
async def code_private_handler(
    event: PrivateMessageEvent, message: Message = CommandArg()
):
    try:
        try:
            await code.finish(await run_code(message))
        except ActionFailed:
            await code.finish(_lang.text("code.too_long", [], str(event.user_id)))
    except FinishedException:
        raise FinishedException()
    except BaseException:
        await _error.report(traceback.format_exc(), code)


# [HELPSTART] Version: 2
# Command: code
# Info: 在线代码运行器
# Msg: 运行代码
# Usage: code <language> [-i <stdin>]\n<代码>
# [HELPEND]
