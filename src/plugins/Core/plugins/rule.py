import json
import os
import os.path
import traceback
from . import _error
from . import _lang
from nonebot import on_command, on_message
from nonebot.adapters.onebot.v11 import Bot, Message
from nonebot.adapters.onebot.v11.event import MessageEvent
from nonebot.exception import FinishedException
from nonebot.log import logger
from nonebot.params import CommandArg

rule = on_message()
ctrlGroup = json.load(open("data/ctrl.json", encoding="utf-8"))["control"]
commands = {}
local = {}
func = on_command("function", aliases={"func", "调用"})


async def runRule(
        bot: Bot,
        event: MessageEvent,
        argument: str,
        code: any,
        handle: any):
    global local, commands
    if isinstance(code, list):
        for c in code:
            if c["调用"] == "eval":
                return eval(c["代码"])  # , __locals=locals())
            elif c["调用"] == "如果真":
                if await runRule(bot, event, argument, c["条件"], handle):
                    await runRule(bot, event, argument, c["执行"], handle)
                elif "否则" in c.keys():
                    await runRule(bot, event, argument, c["否则"], handle)
            elif c["调用"] == "发送消息":
                await handle.send(Message(await runRule(bot, event, argument, c["消息"], handle)))
            elif c["调用"] == "执行":
                exec(c["代码"])  # , __locals=locals())
            elif c["调用"] == "发送控制中心消息":
                await bot.send_group_msg(
                    message=Message(await runRule(bot, event, argument, c["消息"], handle)),
                    group_id=ctrlGroup)
            elif c["调用"] == "取变量":
                return local[c["变量名"]]
            elif c["调用"] == "设置变量":
                local[c["变量名"]] = await runRule(bot, event, argument, c["值"], handle)
            elif c["调用"] == "取字典值":
                return await runRule(bot, event, argument, c["字典"], handle)[c["键"]]
            elif c["调用"] == "删除变量":
                local.pop(c["变量名"])
            elif c["调用"] == "调试输出":
                logger.debug(await runRule(bot, event, argument, c["文本"], handle))
            elif c["调用"] == "尝试":
                try:
                    await runRule(bot, event, argument, c["执行"], handle)
                except BaseException as e:
                    local["_exception"] = e
                    await runRule(bot, event, argument, c["捕获异常"], handle)
                else:
                    if "否则" in runRule.keys():
                        await runRule(bot, event, argument, c["否则"], handle)
            elif c["调用"] == "返回":
                return await runRule(bot, event, argument, c["值"], handle)
            elif c["调用"] == "绑定命令":
                commands[c["命令名"]] = c["执行"]
            else:
                return code
    else:
        return code


def runRuleSync(code: any):
    global local, commands
    if isinstance(code, list):
        for c in code:
            if c["调用"] == "eval":
                return eval(c["代码"])  # , __locals=locals())
            elif c["调用"] == "如果真":
                if runRuleSync(c["条件"]):
                    runRuleSync(c["执行"])
                elif "否则" in c.keys():
                    runRuleSync(c["否则"])
            elif c["调用"] == "执行":
                exec(c["代码"])  # , __locals=locals())
            elif c["调用"] == "取变量":
                return local[c["变量名"]]
            elif c["调用"] == "设置变量":
                local[c["变量名"]] = runRuleSync(c["值"])
            elif c["调用"] == "取字典值":
                return runRuleSync(c["字典"])[c["键"]]
            elif c["调用"] == "删除变量":
                local.pop(c["变量名"])
            elif c["调用"] == "调试输出":
                logger.debug(runRuleSync(c["文本"]))
            elif c["调用"] == "尝试":
                try:
                    runRuleSync(c["执行"])
                except BaseException as e:
                    local["_exception"] = e
                    runRuleSync(c["捕获异常"])
                else:
                    if "否则" in runRule.keys():
                        runRuleSync(c["否则"])
            elif c["调用"] == "返回":
                return runRuleSync(c["值"])
            elif c["调用"] == "绑定命令":
                commands[c["命令名"]] = c["执行"]

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
        # 将rules路径修改为`rules/*`同时忽略`_`开头和非`.json`结尾的文件
        rules = os.listdir("rules")
        # json.load(open("data/rule.rules.json", encoding="utf-8"))
        logger.info(rules)
        argument = event.get_plaintext()
        for r in rules:
            if not r.startswith("_") and r.endswith(".json"):
                ruleData = json.load(
                    open(os.path.join("rules", r), encoding="utf-8"))
                logger.info(_lang.text("rule.run", [ruleData['规则名']]))
                await runRule(bot, event, argument, ruleData['执行'], rule)

        # except FinishedException:
        # raise FinishedException()
    except Exception:
        await _error.report(traceback.format_exc())


@func.handle()
async def funcHandle(
        bot: Bot,
        event: MessageEvent,
        message: Message = CommandArg()):
    try:
        argument = message.extract_plain_text()
        command = argument.split(" ")[0]
        argv = argument.replace(command, "", 1).strip()
        # 处理
        if command in commands.keys():
            await runRule(bot, event, argv, commands[command], func)
        else:
            await func.finish(_lang.text("rule.error", [command], event.get_user_id()))

    except FinishedException:
        raise FinishedException()
    except Exception:
        await _error.report(traceback.format_exc(), func)

# 预处理
rules = os.listdir("rules")
logger.info(rules)
imported = []
for r in rules:
    if not r.startswith("_") and r.endswith(".json"):
        ruleData = json.load(
            open(os.path.join("rules", r), encoding="utf-8"))
        # 导入模块
        if "导入" in ruleData.keys():
            for m in ruleData["导入"]:
                if m not in imported:
                    imported += [m]
                    __import__(m)
        # 运行初始化
        if "初始化" in ruleData.keys():
            logger.info(f"正在执行：{ruleData['规则名']}")
            try:
                runRuleSync(ruleData["初始化"])
            except BaseException:
                logger.error(traceback.format_exc())

# [HELPSTART] Version: 2
# Command: function
# Info: 调用由 XDbot2 Rules 提供的命令
# Msg: 调用规则命令
# Usage: function <命令> [参数]
# [HELPEND]
