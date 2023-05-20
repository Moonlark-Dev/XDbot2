#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os.path


def get_plugin_help(plugin_name: str, module: any) -> dict:
    """
    查找插件帮助
    优先级：注释>commandHelp变量
    """
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "plugins", f"{plugin_name}.py"), encoding="utf-8") as f:
        plugin_file = f.read()
    command_help = dict()
    # 正则表达式出问题了所以用find
    start = plugin_file.find("# [HELPSTART]")
    # 注释写法
    if start != -1:
        # 采集数据
        lines = plugin_file[start:plugin_file.find("# [HELPEND]", start)]
        lines = lines.replace("# ", "").replace("#", "").split("\n")
        if lines[0].find("Version: 2") != -1:
            help_version = 2
        else:
            help_version = 1
        # 版本2
        if help_version == 2:
            now_command = ""
            for line in lines[1:]:
                line_splited = line.split(":")
                # 统一Strip
                for i in range(len(line_splited)):
                    line_splited[i] = line_splited[i].strip()
                # 解析
                if line_splited[0] in ["Command", "命令"]:
                    now_command = line_splited[1]
                    command_help[now_command] = {"usage": []}
                elif line_splited[0] in ["Usage", "用法"]:
                    command_help[now_command]["usage"].append(
                        "\n".join(line_splited[1:]).replace(r"\n", "\n"))
                elif line_splited[0] in ["Info", "描述"]:
                    command_help[now_command]["info"] = "\n".join(line_splited[1]).replace(
                        r"\n", "\n")
                elif line_splited[0] in ["Msg", "概述"]:
                    command_help[now_command]["msg"] = line_splited[1]
        elif help_version == 1:
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
                command_help[commandName] = command
                if "usage" in command.keys():
                    command_help[commandName]["usage"] = command["usage"]
                if "info" in command.keys():
                    command_help[commandName]["info"] = command["info"]
    else:
        command_help = module.commandHelp.copy()
    # 处理CommandHelp
    for key in list(command_help.keys()):
        if "name" not in command_help[key].keys():
            command_help[key]["name"] = str(key)
        if "usage" not in command_help[key].keys():
            command_help[key]["usage"] = [key]
        if "info" not in command_help[key].keys():
            command_help[key]["info"] = "无指令描述"
        if "msg" not in command_help[key].keys():
            command_help[key]["msg"] = command_help[key]["info"]
        if "from" not in command_help[key].keys():
            command_help[key]["from"] = plugin_name
    # 返回
    return command_help
