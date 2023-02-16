from nonebot.adapters.onebot.v11 import Message
from nonebot import on_command, get_driver
from nonebot.adapters.onebot.v11 import MessageEvent
from nonebot.exception import FinishedException
from nonebot.log import logger
from . import _error
import os
import os.path
import json
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
    locals[local_namespace][local_name] = await run_rule(value, namespace)

async def invoke(name, arguments, matcher, namespace):
    # 内置函数
    if name == "send":
        await matcher.send(await run_rule(arguments, namespace))
    elif name == "finish":
        await matcher.finish()

async def run_rule(src, namespace, matcher = None):
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
                if await run_rule(operate["condition"], namespace):
                    await run_rule(operate["run"], namespace)
                else:
                    await run_rule(operate["else"], namespace)
            elif call == "is":
                return await run_rule(operate["a"], namespace) == (await run_rule(operate["b"], namespace))
            elif call == "add":
                return await run_rule(operate["a"], namespace) + (await run_rule(operate["b"], namespace))
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
    file_list = os.listdir("data/rules")
    rule_list = {}
    for filename in file_list:
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
    for rule in rule_list:
        await run_rule(rule["src"], rule["info"]["namespace"])

@func_command.handle()
async def func_command_handler(event: MessageEvent, message: Message = CommandArg()):
    try:
        argv = str(message).split(" ")
        command_args = {}
        command = argv[0].split(":")[1]
        namespace = argv[0].split(":")[0]

        length = 0
        for arg in argv[1:]:
            command_args[commands[namespace][command]["arguments"][length]["name"]] = arg
            length += 1
        for arg in commands[namespace][command]["arguments"][length:]:
            if arg["optional"]:
                command_args[arg["name"]] = arg["default"]
            else:
                await func_command.finish(f"缺少参数：{arg['name']}")

        for key in list(command_args.keys()):
            await set_local(f"args:{key}", command_args[key], namespace)
        for key in list(event.dict().keys()):
            await set_local(f"event:{key}", event.dict()[key], namespace)

        await run_rule(commands[namespace][command]["execute"], func_command, namespace)
        

    except FinishedException:
        raise FinishedException()
    except BaseException:
        await _error.report(traceback.format_exc(), func_command)

