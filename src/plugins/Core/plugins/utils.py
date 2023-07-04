from . import _error as reporter
from . import _lang as lang
from . import _messenger as messenger
from .email import send_email
import nonebot
from nonebot.log import logger
import inspect


def on_command(cmd, **kwargs):
    def _(func):
        nonebot.on_command("cmd", handlers=[func], **kwargs)
    logger.success(f"已注册指令：{cmd}")

    # TODO 完成 utils.py
