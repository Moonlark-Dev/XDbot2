# XDbot2 2023-04-04-19-25

import os
import json

print("欢迎使用：XDbot2")


def move_data(origin_file, file_name):
    data = json.load(open(f"data/etm/{origin_file}", encoding="utf-8"))
    for user in list(data.keys()):
        try:
            os.mkdir(f"data/etm/{user}")
        except BaseException:
            pass
        json.dump(
            data[user],
            open(
                f"data/etm/{user}/{file_name}.json",
                "w",
                encoding="utf-8"))


move_data("achievement.json", "achi")
move_data("achievement_progress.json", "achi_unlock_progress")
move_data("bags.json", "bag")
move_data("users.json", "user")
# move_data("achievement.json", "achi")
