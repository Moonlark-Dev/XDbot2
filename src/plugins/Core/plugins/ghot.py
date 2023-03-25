import json
from time import time
from nonebot import on_command, on_message
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Bot
from nonebot.matcher import Matcher
from . import _lang as lang
from . import _error as error
import traceback

@on_command("ghot", aliases={"群聊热度"}).handle()
async def ghot(bot: Bot, event: GroupMessageEvent, matcher: Matcher):
    try:
        data = json.load(open("data/ghot.data.json", encoding="utf-8"))
        # Clean Data
        now_time = time() 
        for group in list(data.keys()):
            _add = 0
            for l in range(len(data[group])):
                if now_time - data[group][l - _add] >= 600:
                    data[group].pop(l - _add)
                    _add += 1
        # 排序
        groups = []
        for group in list(data.keys()):
            hot = len(data[group])
            is_inserted = False
            for i in range(len(group)):
                if groups[i]["hot"] <= hot:
                    groups.insert(i, {"group": group, "hot": hot})
                    is_inserted = True
            if not is_inserted:
                groups.append({"group": group, "hot": hot})
        # 赋排名
        now_rank = 0
        group_count_in_rank = 1
        now_rank_hot = -1
        this_group_rank = -1
        for i in range(len(groups)):
            if groups[i]["hot"] == now_rank_hot:
                groups[i]["rank"] = now_rank
                group_count_in_rank += 1
            else:
                now_rank_hot = groups[i]["hot"]
                now_rank += group_count_in_rank
                group_count_in_rank = 1
                groups[i]["rank"] = now_rank
            if groups[i]["group"] == str(event.group_id):
                this_group_rank = now_rank
        # 输出
        reply = lang.text("ghot.title", [], event.get_user_id())
        for group in groups[:10]:
            reply += f"{group['rank']}. {(await bot.get_group_info(group_id=group['group']))['group_name']}: {group['hot']}\n"
        await matcher.finish(reply[:-1])

    except BaseException:
        await error.report(traceback.format_exc(), matcher)





@on_message().handle()
async def ghot_writer(event: GroupMessageEvent):
    try:
        data = json.load(open("data/ghot.data.json", encoding="utf-8"))
        try:
            data[str(event.group_id)].append(time())
        except KeyError:
            data[str(event.group_id)] = [time()]
        json.dump(data, open("data/ghot.data.json", "w", encoding="utf-8"))
    except BaseException:
        await error.report(traceback.format_exc())



