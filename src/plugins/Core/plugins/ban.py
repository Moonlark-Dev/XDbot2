from nonebot import *
from fastapi.responses import HTMLResponse
from nonebot.adapters.onebot.v11.event import GroupBanNoticeEvent
from nonebot.adapters.onebot.v11.bot import Bot
import json
import time
import traceback

banCount = on_type(GroupBanNoticeEvent)
ctrlGroup = json.load(open("data/ctrl.json", encoding="utf-8"))["control"]
app = get_app()


@app.get("/ban", response_class=HTMLResponse)
async def homepage():
    bots = get_bots()
    groups = []
    for bot in bots:
        groups += await bots[bot].get_group_list()
    html = "<table border='1'><tr><td>群名称</td><td>群号</td><td>操作</td></tr>"
    for group in groups:
        print(group)
        html += f"<tr><td>{group['group_name']}</td><td>{group['group_id']}</td><td><a href=\"./ban/{group['group_id']}\">查看禁言记录</td>"
    html += "</table>"
    return html


@app.get("/ban/{group_id}", response_class=HTMLResponse)
async def viewBans(group_id):
    data = json.load(open("data/ban.banData.json", encoding="utf-8"))
    html = "<table border='1'><tr><td>用户</td><td>时长</td><td>禁言时间</td><td>解除时间</td><td>操作员</td></tr>"
    for item in data[group_id]:
        if "pardonTime" in item.keys():
            pardonTime = item['pardonTime']
        else:
            pardonTime = item['banTime'] + item['duration']
        html += f"<tr><td>{item['user']['nickname']}({item['user']['user_id']})</td><td>{item['duration']/60}分钟</td><td>{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(item['banTime']))}</td><td>{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(pardonTime))}</td><td>{item['operator']['nickname']}({item['operator']['user_id']})</td></tr>"

    html += "</table>"
    return html


@banCount.handle()
async def banCountHandle(
    bot: Bot,
    event: GroupBanNoticeEvent):
    try:
        data = json.load(open("data/ban.banData.json", encoding="utf-8"))
        event.group_id = str(event.group_id)
        if event.group_id not in data.keys():
            data[event.group_id] = []
        if event.duration != 0:
            data[event.group_id].insert(0, [{
                "user": await bot.get_stranger_info(user_id=event.get_user_id()),
                "duration": event.duration,
                "operator": await bot.get_stranger_info(user_id=event.operator_id),
                "banTime": int(time.time())
            }])
        else:
            nowTime = int(time.time())
            length = 0 
            for item in data[event.group_id]:
                print(
                    item["banTime"] + item["duration"] > nowTime,
                    str(item["user"]["user_id"]) == event.get_user_id(),
                    "pardonTime" not in item.keys()
                )
                if item["banTime"] + item["duration"] > nowTime:
                    if str(item["user"]["user_id"]) == event.get_user_id():
                        if "pardonTime" not in item.keys():
                            data[event.group_id][length]["pardonTime"] = int(time.time())
                            break
                length += 1
        json.dump(data, open("data/ban.banData.json", "w", encoding="utf-8"))
    
    except Exception:
        await bot.send_group_msg(
            group_id=ctrlGroup,
            message=traceback.format_exc()
        )


#app.mount("/ban", webapp)
