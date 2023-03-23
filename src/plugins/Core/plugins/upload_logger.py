from nonebot import on_command
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Bot
from . import _lang
import os.path
import traceback
from . import _error

upload_log = on_command("upload-log", aliases={"上传日志"})


@upload_log.handle()
async def handle(bot: Bot, event: GroupMessageEvent):
    try:
        await bot.call_api(
            api="upload_group_file",
            group_id=event.group_id,
            file=os.path.abspath('./data/error.log'),
            name="error.log"
        )

    except BaseException:
        await _error.report(traceback.format_exc(), upload_log)
