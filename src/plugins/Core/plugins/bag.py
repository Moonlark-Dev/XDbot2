from nonebot import on_command
from nonebot.adapters.onebot.v11.event import MessageEvent
from nonebot.adapters.onebot.v11.bot import Bot, Message
from nonebot.params import CommandArg
from .etm import bag
from . import _lang as lang
from . import _error as error
import traceback

bag_cmd = on_command("bag", aliases={"我的背包", "背包"})

# [HELPSTART]
# !Usage 1 bag
# !Info 1 查看背包
# [HELPEND]

@bag_cmd.handle()
async def show_bag(bot: Bot, event: MessageEvent, message: Message = CommandArg()):
    try:
        argv = str(message).split(" ")
        qq = event.get_user_id()
        data = bag.get_user_bag(qq)

        if argv[0] == "view":
            item = data["data"][int(argv[1])]
            await bag_cmd.finish(lang.text("bag.item_info", [
                item.data["display_name"],
                item.item_id,
                item.count,
                item.data["display_message"]
            ], qq))
        else:
            nickname = (await bot.get_stranger_info(user_id=int(qq)))["nickname"]
            reply = lang.text(
                "bag.title", [nickname, bag.get_items_count_in_bag(qq), 128], qq)
            length = 1
            for item in data:
                reply += f"\n{length}. {item.data['display_name']} x{item.count}"
                length += 1
            await bag_cmd.finish(reply)

    except BaseException:
        await error.report(traceback.format_exc(), bag_cmd)
