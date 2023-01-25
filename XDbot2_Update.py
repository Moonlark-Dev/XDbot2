# XDbot2 v2.2.17-beta

import json

print("欢迎使用：XDbot2 v2.2.17-beta")

data = json.load(open("data/etm.userData.json"))

for key in list(data.keys()):
    try:
        buyTime = data[key]["vip"].pop("buyTime")
        if buyTime:
            data[key]["vip"]["endTime"] = buyTime + 604800
        else:
            data[key]["vip"]["endTime"] = None
    except:
        pass

json.dump(data, open("data/etm.userData.json", "w"))
