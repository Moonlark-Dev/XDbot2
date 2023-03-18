from nonebot import on_command
from nonebot.adapters.onebot.v11.event import MessageEvent
from nonebot.adapters.onebot.v11.bot import Bot
from .etm import user, exp, economy
from . import _lang as lang
from . import _error as error
import traceback

panel = on_command(
        "panel", aliases={"mypanel", "我的面板", "我的数据", "我的信息", "userInfo", "info"})

@panel.handle()
async def show_panel(bot: Bot, event: MessageEvent):
    try:
        qq = event.get_user_id()
        data = user.get_user_data(qq)
        nickname = (await bot.get_stranger_info(user_id=qq))["nickname"]
        level = exp.get_user_level(qq)
        level_max_exp = level ** 2
        bar_filled = int(exp._get_exp(qq) / level_max_exp * 10)

        await panel.finish((
            "「用户信息面板」\n"
            f"{'-'*27}\n"
            f"{nickname}\n"
            f"  等级：Lv{level} ({int(exp.get_exp(qq))} / {(level+1)**2 - level_max_exp})\n"
            f"        [{'=' * max(bar_filled-1, 0)}>{'  ' * (10 - bar_filled)}] {data['exp']}\n"
            f"  余额：{round(data['vimcoin'], 2)}vim ({round(data['vimcoin'] * economy.vimcoin['exchange_rate'], 2)}vi)\n"
            f"  生命值：{data['health']} / 20"))

    except BaseException:
        await error.report(traceback.format_exc())
