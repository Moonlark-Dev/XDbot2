#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

print("XDbot2 更新器 V1.0.0")
with open("XDbot2_Update.py", encoding="utf-8") as f:
    oldVersion = f.read().split("\n")[0]
print(f"当前更新脚本版本标签：{oldVersion}")

print("正在拉取仓库 ...")
print("--- GIT 输出 ---")
os.popen("git pull").read().replace("\n", "\n [I] GIT: ")
print("--- 运行结束 ---")

with open("XDbot2_Update.py", encoding="utf-8") as f:
    script = f.read()
newVersion = script.split("\n")[0]

print(f"更新后更新脚本版本标签：{newVersion}")
if newVersion != oldVersion:
    exec(script)

print("完成！")


