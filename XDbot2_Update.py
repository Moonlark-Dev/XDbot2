# XDbot2 v2.7.37

import os
import json

print("欢迎使用：XDbot2 v2.7.37")

data = json.load(open("data/cave.data.json", "r", encoding="utf-8"))

for key in list(data["data"].keys()):
    if str(data["data"][key]["sender"]) == "269651975":
        data["data"].pop(key)

json.dump(data, open("data/cave.data.json", "w", encoding="utf-8"))
