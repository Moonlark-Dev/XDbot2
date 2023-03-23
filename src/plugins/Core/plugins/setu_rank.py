from nonebot.adapters.onebot.v11 import Message, MessageEvent
from nonebot.adapters.onebot.v11.bot import Bot
from nonebot.exception import FinishedException
from . import _error as error
from . import _lang as lang
from nonebot import on_command
import traceback
import json

setu_rank = on_command("st-l", aliases={"setu-rank", "随机涩图排行榜"})

# [HELPSTART] Version: 2
# Command: st-l
# Usage: st-l
# Msg: 查看全局st-r指令使用排行
# Info: 随机涩图排行
# [HELPEND]

@setu_rank.handle()
async def show_setu_ranking(bot: Bot, event: MessageEvent):
    try:
        data = json.load(open("data/setu.count.json", encoding="utf-8"))
        ranking = []
        for user, count in data.items():
            length = 0
            is_insert = False
            for item in ranking:
                if item["count"] <= count:
                    ranking.insert(length, {"user": user, "count": count})
                    is_insert = True
                    break
                length += 1
            if not is_insert:
                ranking.append({"user": user, "count": count})
        
        now_rank = 0
        users = 1
        my_data = {"user": str(event.user_id), "count": 0, "rank": "999+"}
        max_count = 0
        
        for i in range(len(ranking)):
            if ranking[i]["count"] > max_count:
                now_rank += users
                users = 0
            ranking[i]["rank"] = now_rank
            users += 1
            if ranking[i]["user"] == str(event.user_id):
                my_data = ranking[i]
        
        reply = lang.text("setu_rank.title", [], str(event.user_id))
        for user in ranking[:12]:
            nickname = (await bot.get_stranger_info(user_id=user["user"]))["nickname"]
            reply += f"\n{user['rank']}. {nickname}: {user['count']}"
        reply += "\n" + "-" * 30
        nickname = (await bot.get_stranger_info(user_id=my_data["user"]))["nickname"]
        reply += f"\n{my_data['rank']}. {nickname}: {my_data['count']}"
        
        await setu_rank.finish(reply)
    
    except FinishedException:
        raise FinishedException()
    except BaseException:
        await error.report(traceback.format_exc(), setu_rank)