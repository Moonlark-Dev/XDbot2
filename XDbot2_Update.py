# XDbot2 v2.5.51

import json

print("欢迎使用：XDbot2 v2.5.51-beta")

cavedata = json.load(open("./data/cave.data.json"))

for cave_id in list(cavedata["data"].keys()):
    if "time" not in cavedata["data"][cave_id].keys():
        cavedata["data"][cave_id] = 0.0

json.dump(cavedata, open("./data/cave.data.json", "w"))
