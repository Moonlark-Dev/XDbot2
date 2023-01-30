from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, Message, MessageEvent
from nonebot.params import CommandArg
import os
import marshal
from . import _error
from . import _lang
import random
import traceback

status = False  # [游戏状态] False:待机 True:进行中
number = -1  # [答案数字] -1:待机 其他数字:进行中

guess = on_command("guess", aliases={"gn", "猜数字"})


@guess.handle()
async def guess_handle(bot: Bot, event: MessageEvent, message: Message = CommandArg()):
    try:
        global status, number
        args = message.extract_plain_text().split(" ")
        reply = _lang.text("guess.prefix", [], event.get_user_id())
        if args[0] == "":
            reply += _lang.text("guess.command", [], event.get_user_id())
            await guess.finish(reply)
        elif args[0] == "start":
            if status:
                reply += _lang.text("guess.playing", [], event.get_user_id())
                await guess.finish(reply)
            random.seed(marshal.loads(b"\xe9" + os.urandom(4)))
            number = random.randint(0, 100)
            status = True
            reply += _lang.text("guess.start", [], event.get_user_id())
            await guess.finish(reply)
        else:
            try:
                num = int(args[0])
            except ValueError:
                reply += _lang.text("guess.error_command",
                                    [], event.get_user_id())
                await guess.finish(reply, at_sender=True)
            if not status:
                reply += _lang.text("guess.not_playing",
                                    [], event.get_user_id())
                await guess.finish(reply, at_sender=True)
            if num > 100 or num < 0:
                reply += _lang.text("guess.error_number",
                                    [], event.get_user_id())
                await guess.finish(reply, at_sender=True)
            if num > number:
                reply += _lang.text("guess.too_large",
                                    [args[0]], event.get_user_id())
                await guess.finish(reply, at_sender=True)
            if num < number:
                reply += _lang.text("guess.too_small",
                                    [args[0]], event.get_user_id())
                await guess.finish(reply, at_sender=True)
            if num == number:
                reply += _lang.text(
                    "guess.end",
                    [
                        (await bot.get_stranger_info(user_id=int(event.get_user_id())))[
                            "nickname"
                        ],
                        str(number),
                    ],
                    event.get_user_id(),
                )
                status = False
                number = -1
                await guess.finish(reply)
    except BaseException:
        await _error.report(traceback.format_exc(), guess)
