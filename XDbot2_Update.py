# XDbot2 v2.9-2 23090101152

# /!\ 提示：
# 此文件为 XDbot2 更新脚本，用于更改部分数据以便 XDbot2 正常运行
# 文件第一行为版本标识符，供 XDbot2 Updater 识别版本

import os
import json

for user in os.listdir("data/duel"):
    if os.path.isfile(f"data/duel/{user}"):
        user_data = json.load(open(f"data/duel/{user}", encoding="utf-8"))
        if user_data["ball_level"] == 0:
            user_data["ball_level"] = 1
        json.dump(user_data, open(f"data/duel/{user}", "w", encoding="utf-8"))
