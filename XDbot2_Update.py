# XDbot2 V2.0.0-beta master/af3df071

import os
import json

os.chdir("./data")
data = json.load(open("ban.banData.json", encoding="utf-8"))

for key in list(data.keys()):
    banList = []
    for item in data[key]:
        if type(item) == list:
            banList.append(item[0])
        else:
            banList.append(item)
    data[key] = banList
json.dump(data, open("ban.banData.json", "w", encoding="utf-8"))
print("已重写：data/ban.banData.json")
