# XDbot2 V2.0.0-beta master/8b5ae423

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
