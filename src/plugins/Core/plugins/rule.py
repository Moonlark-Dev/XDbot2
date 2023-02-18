from nonebot.adapters.onebot.v11 import Message
from nonebot import on_command, get_driver
from nonebot.adapters.onebot.v11 import MessageEvent
from nonebot.exception import FinishedException
from nonebot.log import logger
from . import _error
import os
import os.path
import threading
import json
from .rule_compiler import compiler
from . import _lang
import traceback

from nonebot.params import CommandArg

rule_command = on_command("rule", aliases={"规则", "xr"})
func_command = on_command("function", aliases={"func", "调用"})
commands = {}
rules = {}
locals = {}


def register_command(name, namespace, arguments, execute):
    global commands
    commands[name] = {
        "name": name,
        "namespace": namespace,
        "arguments": arguments,
        "execute": execute
    }


def get_local(name, namespace):
    local = name.split(":")
    if len(local) == 1:      # 不含 namespace
        local_namespace = namespace
    else:
        local_namespace = local[0]
    local_name = local[-1]
    return locals[local_namespace][local_name]


async def set_local(name, value, namespace):
    local = name.split(":")
    if len(local) == 1:      # 不含 namespace
        local_namespace = namespace
    else:
        local_namespace = local[0]
    local_name = local[-1]
    if local_namespace not in locals.keys():
        locals[local_namespace] = {}
    locals[local_namespace][local_name] = await run_rule(value, namespace)


async def invoke(name, arguments, matcher, namespace):
    # 内置函数
    if name == "send":
        await matcher.send(await run_rule(arguments, namespace))
    elif name == "finish":
        await matcher.finish()


async def run_rule(src, namespace, matcher=None):
    rule = rules[namespace]
    if type(src) == list:
        for operate in src:
            call = operate["call"]
            if call == "new_command":
                register_command(
                    operate["name"],
                    rule["info"]["namespace_id"],
                    operate["arguments"],
                    operate["run"]
                )
            elif call == "if":
                if await run_rule(operate["condition"], namespace, matcher):
                    await run_rule(operate["run"], namespace, matcher)
                else:
                    await run_rule(operate["else"], namespace, matcher)
            elif call == "is":
                return await run_rule(operate["a"], namespace, matcher) == (await run_rule(operate["b"], namespace, matcher))
            elif call == "add":
                return await run_rule(operate["a"], namespace, matcher) + (await run_rule(operate["b"], namespace, matcher))
            elif call == "get_var":
                return get_local(operate["name"], namespace)
            elif call == "set":
                await set_local(operate["name"], operate["value"], namespace)
            elif call == "invoke":
                await invoke(operate["function"], operate["arguments"], matcher, namespace)
    else:
        return src


@get_driver().on_startup
async def init_rules():
    global rules
    file_list = os.listdir("data/rules")
    rule_list = {}
    for filename in file_list:
        if filename[:-4] not in rule_list.keys():
            rule_list[filename[:-4]] = {}
        if filename.endswith(".xrc"):
            rule_list[filename[:-4]]["src"] = json.load(
                open(os.path.join("./data/rules", filename), encoding="utf-8"))
        elif filename.endswith(".xri"):
            rule_list[filename[:-4]]["info"] = json.load(
                open(os.path.join("./data/rules", filename), encoding="utf-8"))
    for rule in list(rule_list.keys()):
        if "src" not in rule_list[rule].keys(
        ) or "info" not in rule_list[rule].keys():
            rule_list.pop(rule)
    # rules = rule_list
    for rule in list(rule_list.values()):
        rules[rule["info"]["namespace_id"]] = rule.copy()
    logger.info(rules)
    for rule in list(rules.values()):
        logger.info(rule["src"])
        await run_rule(rule["src"], rule["info"]["namespace_id"])


@func_command.handle()
async def func_command_handler(event: MessageEvent, message: Message = CommandArg()):
    try:
        argv = str(message).split(" ")
        command_args = {}
        command = argv[0]
        # namespace = argv[0].split(":")[0]
        namespace = commands[command]["namespace"]

        logger.info(commands)

        length = 0
        for arg in argv[1:]:
            command_args[commands[command]
                         ["arguments"][length]["name"]] = arg
            length += 1
        for arg in commands[command]["arguments"][length:]:
            if arg["optional"]:
                command_args[arg["name"]] = arg["default"]
            else:
                await func_command.finish(_lang.text("rule.needargv"), [arg['name']], event.get_user_id())

        for key in list(command_args.keys()):
            await set_local(f"args:{key}", command_args[key], namespace)
        for key in list(event.dict().keys()):
            await set_local(f"event:{key}", event.dict()[key], namespace)

        await run_rule(commands[command]["execute"],  namespace, func_command)

    except FinishedException:
        raise FinishedException()
    except BaseException:
        await _error.report(traceback.format_exc(), func_command)


@rule_command.handle()
async def rule_handler(event: MessageEvent, message: Message = CommandArg()):
    try:
        argument = str(message).split("\n")[0].split(" ")
        if argument[0] in ["build", "编译"]:
            if json.load(open(os.path.join("./data/rules", f"{argument[1]}.info.json")))["user_id"] == event.get_user_id():
                threading.Thread(target=lambda: compiler.build(
                    f"./data/rules/{argument[1]}")).start()
                await rule_command.finish(_lang.text("rule.finish", [], event.get_user_id()))
            else:
                await rule_command.finish(_lang.text("rule.noprimission", [], event.get_user_id()))
        elif argument[0] in ["create", "创建"]:
            json.dump({"user_id": event.get_user_id()}, open(
                os.path.join("./data/rules", f"{argument[1]}.info.json"), "w"))
            await rule_command.finish(_lang.text("rule.cteated", [], event.get_user_id()))
        elif argument[0] in ["edit", "编辑"]:
            if json.load(open(os.path.join("./data/rules", f"{argument[1]}.info.json")))["user_id"] == event.get_user_id():
                with open(os.path.join("./data/rules", f"{argument[1]}.xr"), "w") as f:
                    f.write("\n".join(str(message).split("\n")[1:]))
                await rule_command.finish(_lang.text("rule.finish", [], event.get_user_id()))
            else:
                await rule_command.finish(_lang.text("rule.noprimission", [], event.get_user_id()))
        elif argument[0] in ["reload", "重载"]:
            await init_rules()
            await rule_command.finish(_lang.text("rule.finish", [], event.get_user_id()))
        elif argument[0] in ["remove", "删除"]:
            if json.load(open(os.path.join("./data/rules", f"{argument[1]}.info.json")))["user_id"] == event.get_user_id():
                files = os.listdir("./data/ruleis")
                for file in files:
                    if file in [f"{argument[1]}.info.json", f"{argument[1]}.xrc", f"{argument[1]}.xri", f"{argument[1]}.xr"]:
                        os.remove(os.path.join("./data/rules", file))
                await rule_command.finish(_lang.text("rule.finish", [], event.get_user_id()))
            else:
                await rule_command.finish(_lang.text("rule.noprimission", [], event.get_user_id()))
        elif argument[0] in ["list", "ls", "查看所有"]:
            await rule_command.finish(_lang.text("rule.list", [list(rules.keys())], event.get_user_id()))
        elif argument[0] in ["get", "view", "查看"]:
            with open(os.path.join("./data/rules", f"{argument[1]}.xr")) as f:
                await rule_command.finish(f.read())
        



    except FinishedException:
        raise FinishedException()
    except BaseException:
        await _error.report(traceback.format_exc(), rule_command)
