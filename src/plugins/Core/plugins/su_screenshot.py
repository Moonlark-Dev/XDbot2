from nonebot.adapters.onebot.v11 import Message
from nonebot.params import CommandArg
from .su import su
import traceback
from . import _error
import os.path
from nonebot.log import logger
try:
    import pyautogui
except BaseException:
    logger.warning("可选依赖 pyautogui 未安装")


@su.handle()
async def screenshot(message: Message = CommandArg()):
    argument = str(message).split(" ")
    try:
        if argument[0] in ["截图", "screenshot"]:
            try:
                os.remove("data/screenshot.png")
            except BaseException:
                pass
            try:
                pyautogui.screenshot("data/screenshot.png")
            except NameError:
                await su.send("错误：可选依赖 pyautogui 未安装")
            except OSError:
                await su.send("失败：无法截图")
            else:
                await su.send(
                    Message(
                        f"[CQ:image,file=file://{os.path.abspath('./data/screenshot.png')}]"
                    )
                )
    except BaseException:
        await _error.report(traceback.format_exc(), su)
