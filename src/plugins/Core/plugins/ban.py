import json
import time
import traceback
from . import _error
from fastapi.responses import HTMLResponse
from nonebot import get_app, get_bots, on_type
from nonebot.adapters.onebot.v11.bot import Bot
from nonebot.adapters.onebot.v11.event import GroupBanNoticeEvent

banCount = on_type(GroupBanNoticeEvent)
ctrlGroup = json.load(open("data/ctrl.json", encoding="utf-8"))["control"]
app = get_app()


def formatHtml(html: str) -> str:
    return f"""<!DOCTYPE html>
<html>
    <head>
        <meta charset="utf-8">
        <title>XDbot2</title>
    </head>
    <body>
        {html}
        <footer>
            <p>Powered by <a href="https://github.com/This-is-XiaoDeng/XDbot2">XDbot2</a></p>
        </footer>
    </body>
</html>"""


@app.get("/ban", response_class=HTMLResponse)
async def homepage() -> str:
    try:
        bots = get_bots()
        groups = []
        for bot in bots:
            groups += await bots[bot].get_group_list()
        html = "<table border='1'><tr><td>群名称</td><td>群号</td><td>操作</td></tr>"
        addedGroup = []
        for group in groups:
            if group["group_id"] not in addedGroup:
                html += f"<tr><td>{group['group_name']}</td><td>{group['group_id']}</td><td><a href=\"./ban/{group['group_id']}\">查看禁言记录</td>"
                addedGroup.append(group["group_id"])
        html += "</table>"
        return f"""<!DOCTYPE html>
<html>
    <head>
        <meta charset="utf-8">
        <title>XDbot2</title>
    </head>
    <body>
        {html}
        <footer>
            <p>Powered by <a href="https://github.com/This-is-XiaoDeng/XDbot2">XDbot2</a></p>
        </footer>
    </body>
</html>"""
    except BaseException:
        await _error.report(traceback.format_exc())
        formatHtml(
            (
                "<h1>服务器内部错误</h1>"
                "<p>给老子去："
                "https://github.com/This-is-XiaoDeng/XDbot2/issues/new?assignees=&labels=%C2%B7+Bug&template=bug.yml"
                " 提交 Issue </p>"
            )
        )


@app.get("/ban/{group_id}", response_class=HTMLResponse)
async def viewBans(group_id) -> str:
    try:
        data = json.load(open("data/ban.banData.json", encoding="utf-8"))
        html = "<table border='1'><tr><td>用户</td><td>时长</td><td>禁言时间</td><td>解除时间</td><td>操作员</td></tr>"
        try:
            for i in data[group_id]:
                # 类型转换处理（我写了个啥……）
                if isinstance(i, list):
                    item = i[0]
                else:
                    item = i
                if "pardonTime" in item.keys():
                    pardonTime = item["pardonTime"]
                else:
                    pardonTime = item["banTime"] + item["duration"]
                html += f"<tr><td>{item['user']['nickname']}({item['user']['user_id']})</td><td>{item['duration']/60}分钟</td><td>{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(item['banTime']))}</td><td>{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(pardonTime))}</td><td>{item['operator']['nickname']}({item['operator']['user_id']})</td></tr>"

            html += "</table>"
        except KeyError:
            html = "啊哦，好像并没有这个呢"
        return formatHtml(html)
    except BaseException:
        _error.report(traceback.format_exc())
        return formatHtml(
            (
                "<h1>你吗你给服务器搞踏马炸了</h1>"
                "<p>给老子滚去："
                "https://github.com/This-is-XiaoDeng/XDbot2/issues/new?assignees=&labels=%C2%B7+Bug&template=bug.yml"
                " 提交 Issue </p>"
            )
        )


@banCount.handle()
async def banCountHandle(bot: Bot, event: GroupBanNoticeEvent) -> None:
    try:
        data = json.load(open("data/ban.banData.json", encoding="utf-8"))
        event.group_id = str(event.group_id)
        if event.group_id not in data.keys():
            data[event.group_id] = []
        if event.duration != 0:
            data[event.group_id].insert(
                0,
                {
                    "user": await bot.get_stranger_info(user_id=event.get_user_id()),
                    "duration": event.duration,
                    "operator": await bot.get_stranger_info(user_id=event.operator_id),
                    "banTime": int(time.time()),
                },
            )
        else:
            nowTime = int(time.time())
            length = 0
            for item in data[event.group_id]:
                print(
                    item["banTime"] + item["duration"] > nowTime,
                    str(item["user"]["user_id"]) == event.get_user_id(),
                    "pardonTime" not in item.keys(),
                )
                if item["banTime"] + item["duration"] > nowTime:
                    if str(item["user"]["user_id"]) == event.get_user_id():
                        if "pardonTime" not in item.keys():
                            data[event.group_id][length]["pardonTime"] = int(
                                time.time()
                            )
                            break
                length += 1
        json.dump(data, open("data/ban.banData.json", "w", encoding="utf-8"))

    except Exception:
        await _error.report(traceback.format_exc())
