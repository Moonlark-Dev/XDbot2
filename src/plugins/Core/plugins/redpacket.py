from math import e
import random
from nonebot import get_driver, on_regex
from ._utils import *
from nonebot.adapters.onebot.v11.bot import Bot
from .etm import economy
from .etm import data as etm_data
from .email import send_email

# [HELPSTART] Version: 2
# Command: mrp
# Info: 发红包
# Usage: mrp <总金额> <个数>
# [HELPEND]

redpackets = {}


@get_driver().on_shutdown
async def repay_vimcoin():
    for redpacket in list(redpackets.values()):
        economy.add_vimcoin(redpacket[0], redpacket[1])
        await send_email(
            str(redpacket[0]),
            lang.text("redpacket.repay_subject", [], redpacket[0]),
            lang.text("redpacket.repay_message", [redpacket[1]], redpacket[0]),
        )
    etm_data.save_data()


@on_command("mrp", aliases={"make-red-packet", "发红包"}).handle()
async def handle_mrp_command(
    bot: Bot, event: GroupMessageEvent, message: Message = CommandArg()
):
    try:
        argv = message.extract_plain_text().split(" ")
        argv[0] = max(float(argv[0]), 0.001)  # type: ignore

        if not economy.use_vimcoin(event.get_user_id(), argv[0]):
            await finish("currency.no_money", [argv[0]], event.user_id)
        message_id = (
            await bot.send_group_msg(
                group_id=event.group_id,
                message=Message(
                    lang.text("redpacket.info", [event.user_id], event.user_id)
                ),
            )
        )["message_id"]
        redpackets[message_id] = [event.user_id, argv[0]]
        try:
            remainder_count = max(int(argv[1]), 1)
        except:
            remainder_count = 1
        claimed_user = []

        @on_regex("抢").handle()
        async def _(matcher: Matcher, subevent: GroupMessageEvent):
            nonlocal remainder_count
            try:
                if not subevent.reply:
                    await matcher.finish()
                if (
                    subevent.user_id not in claimed_user
                    and subevent.reply.message_id == message_id
                ):
                    vimcoin_count = (
                        (
                            round(
                                random.random()
                                * 1000
                                % (redpackets[message_id][1] / 2),
                                3,
                            )
                        )
                        if remainder_count > 1
                        else redpackets[message_id][1]
                    )
                    economy.add_vi(subevent.user_id, vimcoin_count)
                    remainder_count -= 1
                    redpackets[message_id][1] -= vimcoin_count
                    claimed_user.append(subevent.user_id)
                    await matcher.send(
                        Message(
                            lang.text(
                                "redpacket.open",
                                [event.user_id, vimcoin_count],
                                subevent.user_id,
                            )
                        ),
                        at_sender=True,
                    )
                    if remainder_count == 0:
                        await send_text(
                            "redpacket.finish", [event.user_id], event.user_id
                        )
                        redpackets.pop(message_id)
                        matcher.destroy()
            except:
                await error.report()

    except:
        await error.report()
