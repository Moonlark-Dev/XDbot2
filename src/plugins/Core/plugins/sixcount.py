import json
import time
import traceback

from fastapi.responses import HTMLResponse
from pyecharts import options as opts
from pyecharts.charts import Pie

from nonebot.adapters.onebot.v11 import MessageEvent, Bot
from nonebot.matcher import Matcher
from nonebot import on_startswith, on_command
from nonebot import get_bots, get_app

from . import _lang as lang
from . import _error

ctrl_group = json.load(open("data/ctrl.json", encoding="utf-8"))["control"]
on_six = on_startswith("6")
app = get_app()


@on_command("6-count").handle()
async def _(matcher: Matcher, event: MessageEvent, bot: Bot):
    try:
        data = json.load(open("data/sixcount.data.json", encoding="utf-8"))
        sorted_data = sorted(data.items(), key=lambda x: x[1], reverse=True)
        s = lang.text("sixcount.title", [], event.get_user_id()) + "\n"
        n = 1
        for user_id, count in sorted_data[:10]:
            nickname = (await bot.get_stranger_info(user_id=int(user_id)))["nickname"]
            s += f"{n}. {nickname}: {count}\n"
            n += 1
        s += "-" * 30 + "\n"
        user_id = event.get_user_id()
        count = data[user_id]
        for i in range(len(sorted_data)):
            if sorted_data[i][0] == user_id:
                nickname = (await bot.get_stranger_info(user_id=int(user_id)))["nickname"]
                s += f"{i + 1}. {nickname}: {count}"
                break
        await matcher.send(s)
    except Exception:
        await _error.report(traceback.format_exc(), matcher)


@on_six.handle()
async def on_six_handle(event: MessageEvent) -> None:
    """「6」计数器"""
    try:
        data = json.load(open("data/sixcount.data.json", encoding="utf-8"))
        userID = event.get_user_id()
        if userID == "1226383994":
            userID = "2558938020"
        try:
            data[userID] += 1
        except KeyError:
            data[userID] = 1
        json.dump(data, open("data/sixcount.data.json", "w", encoding="utf-8"))

    except Exception:
        await _error.report(traceback.format_exc())


@app.get("/six/data.json")
async def get_data() -> dict | None:
    """从Web获取数据"""
    try:
        return json.load(open("data/sixcount.data.json", encoding="utf-8"))
    except Exception:
        await _error.report(traceback.format_exc())


@app.get("/six/startime.json")
async def get_start_time() -> dict | None:
    """从Web获取开始时间"""
    try:
        return json.load(
            open("data/sixcount.starttime.json", encoding="utf-8"))
    except Exception:
        await _error.report(traceback.format_exc())


@app.get("/six/full", response_class=HTMLResponse)
async def pie():
    """生成并反回饼图"""
    try:
        data = json.load(open("data/sixcount.data.json", encoding="utf-8"))
        start_time = time.strftime(
            "%Y-%m-%d %H:%M:%S",
            time.localtime(
                json.load(
                    open("data/sixcount.starttime.json", encoding="utf-8"))["time"]),
        )

        user_data = []
        bots = get_bots()
        bot = bots[list(bots.keys())[0]]
        user_list = list(data.keys())

        for i in range(len(user_list)):

            user_data.append(
                (
                    (await bot.get_stranger_info(user_id=user_list[i]))["nickname"],
                    data[user_list[i]],
                )
            )

        file_path = (
            Pie(init_opts=opts.InitOpts(bg_color="rgba(255,255,255,1)"))
            .add("", user_data)
            .set_global_opts(
                title_opts=opts.TitleOpts(
                    title="6", subtitle=start_time + " 至今"),
                legend_opts=opts.LegendOpts(is_show=False))

            .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}"))
        ).render(path="data/sixcount.render.ro.html")

        with open(file_path, encoding="utf-8") as f:
            html = f.read()

        return html
    except Exception:
        await _error.report(traceback.format_exc())


@app.get("/six", response_class=HTMLResponse)
async def pie():
    """生成并反回饼图"""
    try:
        data = json.load(open("data/sixcount.data.json", encoding="utf-8"))
        start_time = time.strftime(
            "%Y-%m-%d %H:%M:%S",
            time.localtime(
                json.load(
                    open("data/sixcount.starttime.json", encoding="utf-8"))["time"]),
        )

        user_data = []
        bots = get_bots()
        bot = bots[list(bots.keys())[0]]
        user_list = list(data.keys())
        other_count = 0

        for i in range(len(user_list)):
            # See https://github.com/ITCraftDevelopmentTeam/XDbot2/issues/245
            if len(user_list) >= 20 and data[user_list[i]] <= 10:
                other_count += data[user_list[i]]
            else:
                user_data.append(
                    (
                        (await bot.get_stranger_info(user_id=user_list[i]))["nickname"],
                        data[user_list[i]],
                    )
                )
        if other_count > 0:
            user_data.append((
                "Other", other_count
            ))

        file_path = (
            Pie(init_opts=opts.InitOpts(bg_color="rgba(255,255,255,1)"))
            .add("", user_data)
            .set_global_opts(
                title_opts=opts.TitleOpts(
                    title="6", subtitle=start_time + " 至今"),
                legend_opts=opts.LegendOpts(is_show=False))

            .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}"))
        ).render(path="data/sixcount.render.ro.html")

        with open(file_path, encoding="utf-8") as f:
            html = f.read()

        return html
    except Exception:
        await _error.report(traceback.format_exc())
