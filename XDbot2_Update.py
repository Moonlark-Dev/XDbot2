# XDbot2 v2.9-2 2309091455

# /!\ 提示：
# 此文件为 XDbot2 更新脚本，用于更改部分数据以便 XDbot2 正常运行
# 文件第一行为版本标识符，供 XDbot2 Updater 识别版本

import os
import json

for user in os.listdir("data/etm"):
    if os.path.isfile(f"data/etm/{user}/user.json"):
        user_data = json.load(open(f"data/etm/{user}/user.json", encoding="utf-8"))
        user_data["health"] = 1145141919810
        json.dump(user_data, open(f"data/etm/{user}/user.json", "w", encoding="utf-8"))
