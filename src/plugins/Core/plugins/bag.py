from nonebot import on_command
from nonebot.adapters.onebot.v11.event import MessageEvent
from nonebot.adapters.onebot.v11.bot import Bot
from .etm import bag
from . import _lang as lang
from . import _error as error
import traceback

bag_cmd = on_command("bag", aliases={"我的背包", "背包"})

@bag_cmd.handle()
async def show_bag(bot: Bot, event: MessageEvent):
    try:
        qq = event.get_user_id()
        data = bag.get_user_bag()
        nickname = (await bot.get_stranger_info(user_id=qq))["nickname"]
        reply = f"「{nickname}的背包（{len(data)} / 256）」\n"
        length = 0
        for item in data:
            reply += f"{length}. {item.data['display_name']} x{item.count}\n"
            length += 1
        await bag_cmd.finish(reply)

    except BaseException:
        await error.report(traceback.format_exc())
