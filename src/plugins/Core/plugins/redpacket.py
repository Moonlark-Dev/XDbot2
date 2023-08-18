from math import e
import random
from nonebot import on_regex
from ._utils import *
from nonebot.adapters.onebot.v11.bot import Bot
from .etm import economy

@on_command("mrp", aliases={"make-red-packet"}).handle()
async def handle_mrp_command(bot: Bot, event: GroupMessageEvent, message: Message = CommandArg()):
    try:
        argv = message.extract_plain_text().split(" ")
        if not economy.use_vimcoin(event.get_user_id(), float(argv[0])):
            await finish("currency.no_money", [argv[0]], event.user_id)
        message_id = (await bot.send_group_msg(
            group_id=event.group_id,
            message=Message(lang.text("redpacket.info", [event.user_id], event.user_id))
        ))["message_id"]
        remainder_vimcoin = float(argv[0])
        try:
            remainder_count = int(argv[1])
        except:
            remainder_count = 1
        claimed_user = []
        
        @on_regex("抢").handle()
        async def _(matcher: Matcher, subevent: GroupMessageEvent):
            nonlocal remainder_count, remainder_vimcoin
            try:
                if subevent.group_id == event.group_id and subevent.user_id not in claimed_user:
                    vimcoin_count = (round(random.random() % remainder_vimcoin, 3)) if remainder_count >= 0 else remainder_vimcoin
                    economy.add_vi(subevent.user_id, vimcoin_count)
                    remainder_count -= 1
                    remainder_vimcoin -= vimcoin_count
                    claimed_user.append(subevent.user_id)
                    await send_text("redpacket.open", [event.user_id, vimcoin_count], subevent.user_id, at_sender=True)
                    if remainder_count == 0:
                        await send_text("redpacket.finish", [event.user_id], event.user_id)
                        matcher.destroy()
            except:
                await error.report()



    except:
        await error.report()