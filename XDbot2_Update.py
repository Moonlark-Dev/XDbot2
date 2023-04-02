# XDbot2 v2.7.37

import os
import json

print("欢迎使用：XDbot2 v2.7.37")

data = json.load(open("data/cave.data.json", "r", encoding="utf-8"))
# print(data)
for key in list(data["data"].keys()):
    print(key, data["data"][key]["sender"])
    if data["data"][key]["sender"] == "2696519745":
        data["data"].pop(key)
        print("removed", key)

json.dump(data, open("data/cave.data.json", "w", encoding="utf-8"))
