from nonebot.adapters.onebot.v11 import Bot
from nonebot.adapters.onebot.v11 import Message
from nonebot.adapters.onebot.v11.event import MessageEvent
# from nonebot.params import CommandArg
from nonebot import on_message
# from nonebot.exception import FinishedException
from nonebot.log import logger
import json
import os
import traceback

rule = on_message()
ctrlGroup = json.load(open("data/ctrl.json", encoding="utf-8"))["control"]
local = {}


async def runRule(
        bot: Bot,
        event: MessageEvent,
        argument: str,
        code: list | str):
    global local
    if isinstance(code, list):
        for c in code:
            if c["调用"] == "eval":
                return eval(c["代码"])  # , __locals=locals())
            elif c["调用"] == "如果真":
                if await runRule(bot, event, argument, c["条件"]):
                    await runRule(bot, event, argument, c["执行"])
            elif c["调用"] == "发送消息":
                await rule.send(Message(await runRule(bot, event, argument, c["消息"])))
            elif c["调用"] == "执行":
                exec(c["代码"])  # , __locals=locals())
            elif c["调用"] == "发送控制中心消息":
                await bot.send_group_msg(
                    message=Message(await runRule(bot, event, argument, c["消息"])),
                    group_id=ctrlGroup)
            elif c["调用"] == "取变量":
                return local[c["变量名"]]
            elif c["调用"] == "设置变量":
                local[c["变量名"]] = await runRule(bot, event, argument, c["值"])
            elif c["调用"] == "取字典值":
                return await runRule(bot, event, argument, c["字典"])[c["键"]]
            else:
                return code
    else:
        return code


@rule.handle()
async def ruleHandle(
        bot: Bot,
        event: MessageEvent):
    try:
        # logger.info("nmslnmslnmsl")
        rules = json.load(open("data/rule.rules.json", encoding="utf-8"))
        logger.info(rules)
        argument = event.get_plaintext()
        for r in rules:
            logger.info(f"正在执行：{r['规则名']}")
            await runRule(bot, event, argument, r['执行'])

        # except FinishedException:
        # raise FinishedException()
    except Exception:
        await bot.send_group_msg(
            message=traceback.format_exc(),
            group_id=ctrlGroup
        )
