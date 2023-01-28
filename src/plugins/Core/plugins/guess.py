from nonebot import on_command
from nonebot.adapters.onebot.v11 import (Bot, Message, MessageEvent)
from nonebot.params import CommandArg
import os
import marshal
from . import _error
import random
import traceback

status = False  # [游戏状态] False:待机 True:进行中
number = -1  # [答案数字] -1:待机 其他数字:进行中

guess = on_command("guess", aliases={"gn", "猜数字"})


@guess.handle()
async def guess_handle(bot: Bot,
                       event: MessageEvent,
                       message: Message = CommandArg()):
    try:
        global status, number
        args = message.extract_plain_text().split(" ")
        reply = "[猜数字] "
        if args[0] == "":
            reply += "请使用 /guess start 发起一轮游戏"
            await guess.finish(reply)
        elif args[0] == "start":
            if status:
                reply += "有正在进行中的游戏，请等待结束再发起"
                await guess.finish(reply)
            random.seed(marshal.loads(b'\xe9' + os.urandom(4)))
            number = random.randint(0, 100)
            status = True
            reply += "游戏已开始，请使用 /guess <number> 参与，数字为0~100的整数"
            await guess.finish(reply)
        else:
            try:
                num = int(args[0])
            except ValueError:
                reply += "无效命令"
                await guess.finish(reply, at_sender=True)
            if not status:
                reply += "并没有进行中的游戏，阁下可以试试 /guess start "
                await guess.finish(reply, at_sender=True)
            if num > 100 or num < 0:
                reply += "无效数字"
                await guess.finish(reply, at_sender=True)
            if num > number:
                reply += f"{args[0]} 太大了"
                await guess.finish(reply, at_sender=True)
            if num < number:
                reply += f"{args[0]} 太小了"
                await guess.finish(reply, at_sender=True)
            if num == number:
                reply += f"{(await bot.get_stranger_info(user_id=int(event.get_user_id())))['nickname']} 率先猜对了答案为 {str(number)} ！游戏结束"
                status = False
                number = -1
                await guess.finish(reply)
    except BaseException:
        await _error.report(traceback.format_exc(), guess)
