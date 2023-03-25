from nonebot.adapters.onebot.v11 import Bot, Message, MessageEvent
from nonebot.params import CommandArg
from .su import su
from nonebot.log import logger
import time
import json
import os.path


@su.handle()
async def write_su_logger(bot: Bot, event: MessageEvent, message: Message = CommandArg()):
    log_msg = str(message)
    logger.debug(f"[su] 用户 {event.get_user_id()} 使用：{message}")
    try:
        if not log_msg.split(" ")[0] in ["log", "日志", "审核日志", "查看日志", "*log"]:
            if not os.path.exists("data/su.log.json"):
                json.dump([], open("data/su.log.json", "w", encoding="utf-8"))
            log = json.load(open("data/su.log.json", encoding="utf-8"))
            log_time = time.localtime()
            log.append({
                "user": {
                    "id": event.get_user_id(),
                    "name": (await bot.get_stranger_info(user_id=int(event.get_user_id())))["nickname"],
                    "group": event.get_session_id().split("_")[1]
                },
                "time": {
                    "Y": time.strftime("%Y", log_time),
                    "M": time.strftime("%m", log_time),
                    "D": time.strftime("%d", log_time),
                    "h": time.strftime("%H", log_time),
                    "m": time.strftime("%M", log_time),
                    "s": time.strftime("%S", log_time)
                },
                "command": log_msg
            })
            json.dump(log, open("data/su.log.json", "w", encoding="utf-8"))
    except BaseException:
        logger.warning("[WARN] 记录su审核日志失败")
