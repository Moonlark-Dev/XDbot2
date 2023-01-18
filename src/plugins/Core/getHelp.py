#!/usr/bin/env python
# -*- coding: utf-8 -*-

# import re
# import json
import os.path
# from nonebot.log import logger


def getPluginHelp(pluginName: str, module: any):
    """
    查找插件帮助
    优先级：注释>commandHelp变量
    """
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "plugins", f"{pluginName}.py"), encoding="utf-8") as f:
        pluginFile = f.read()
    commandHelp = dict()
    # 正则表达式出问题了所以用find
    start = pluginFile.find("# [HELPSTART]")
    # 注释写法
    if start != -1:
        # 采集数据
        lines = pluginFile[start:pluginFile.find("# [HELPEND]", start)]
        lines = lines.replace("# ", "").replace("#", "").split("\n")
        if lines[0].find("Version: 2") != -1:
            helpVersion = 2
        else:
            helpVersion = 1
        # 版本2
        if helpVersion == 2:
            nowCommand = ""
            for line in lines[1:]:
                l = line.split(":")
                # 统一Strip
                for i in range(len(l)):
                    l[i] = l[i].strip()
                # 解析
                if l[0] in ["Command", "命令"]:
                    nowCommand = l[1]
                    commandHelp[nowCommand] = {"usage": []}
                elif l[0] in ["Usage", "用法"]:
                    commandHelp[nowCommand]["usage"].append(
                        l[1].replace(r"\n", "\n"))
                elif l[0] in ["Info", "描述"]:
                    commandHelp[nowCommand]["info"] = l[1].replace(r"\n", "\n")
                elif l[0] in ["Msg", "概述"]:
                    commandHelp[nowCommand]["msg"] = l[1]
        elif helpVersion == 1:
            commands = dict()
            # print(lines[1:])
            for line in lines[1:]:
                if line == "":
                    continue
                lineSplited = line.split(" ")
                if lineSplited[1] not in commands.keys():
                    commands[lineSplited[1]] = {"usage": []}
                # 处理
                if lineSplited[0] == "!Usage":
                    commands[lineSplited[1]]["usage"].append(line.replace(
                        f"!Usage {lineSplited[1]}", "").strip().replace(r"\n", "\n"))
                elif lineSplited[0] == "!Info":
                    commands[lineSplited[1]]["info"] = line.replace(
                        f"!Info {lineSplited[1]}", "").strip().replace(r"\n", "\n")
            for key in list(commands.keys()):
                command = commands[key]
                commandName = command["usage"][0].split(" ")[0]
                commandHelp[commandName] = command
                if "usage" in command.keys():
                    commandHelp[commandName]["usage"] = command["usage"]
                if "info" in command.keys():
                    commandHelp[commandName]["info"] = command["info"]
    else:
        commandHelp = module.commandHelp.copy()
    # 处理CommandHelp
    for key in list(commandHelp.keys()):
        if "name" not in commandHelp[key].keys():
            commandHelp[key]["name"] = str(key)
        if "usage" not in commandHelp[key].keys():
            commandHelp[key]["usage"] = [key]
        if "info" not in commandHelp[key].keys():
            commandHelp[key]["info"] = "无指令描述"
        if "msg" not in commandHelp[key].keys():
            commandHelp[key]["msg"] = commandHelp[key]["info"]
        if "from" not in commandHelp[key].keys():
            commandHelp[key]["from"] = pluginName
    # 返回
    return commandHelp
