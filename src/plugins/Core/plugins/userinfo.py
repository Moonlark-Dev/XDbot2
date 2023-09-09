from nonebot import on_command
from nonebot.adapters.onebot.v11.event import MessageEvent
from nonebot.adapters.onebot.v11.bot import Bot
from .etm import user, exp, economy, health
from .etm.data import basic_data
from . import _lang as lang
from . import _error as error
import traceback

panel = on_command("panel", aliases={"mypanel", "我的面板", "我的数据", "我的信息", "userInfo"})


@panel.handle()
async def show_panel(bot: Bot, event: MessageEvent):
    try:
        qq = event.get_user_id()
        data = user.get_user_data(qq)
        nickname = (await bot.get_stranger_info(user_id=qq))["nickname"]
        level = exp.get_user_level(qq)
        # level_max_exp = level ** 2
        bar_filled = int(exp.get_exp(qq) / (level**2 - (level - 1) ** 2) * 10)
        # 获取排行
        _data = []
        for u, d in list(basic_data.items()):
            _data.append({"user": u, "vimcoin": d["vimcoin"]})
        _data = sorted(_data, key=lambda x: x["vimcoin"], reverse=True)
        _rk = _data.index({"user": qq, "vimcoin": data["vimcoin"]})
        # 发送
        await panel.send(
            (
                f"{lang.text('userinfo.title', [], qq)}\n"
                f"—————————————\n"
                f"{nickname}({qq})\n"
                f"  {lang.text('userinfo.level', [], qq)}：Lv{level} ({int(exp.get_exp(qq))} / {(level)**2 - (level-1)**2} exp)\n"
                f"        [{'=' * max(bar_filled-1, 0)}>{'  ' * (10 - bar_filled)}]\n"
                f"  {lang.text('userinfo.vimcoin', [], qq)}：{round(data['vimcoin'], 2)}vim (No. {_rk + 1})\n"
                f"  {lang.text('userinfo.health', [], qq)}：{data['health']} / {health.get_max_hp(event.user_id)}"
            )
        )

    except BaseException:
        await error.report(traceback.format_exc(), panel)
