import asyncio
from ._utils import *
from .etm.health import get_max_hp
from .etm.duel.entity.user import User
from nonebot.rule import to_me
from .etm.duel.scheduler import Scheduler


# [HELPSTART] Version: 2
# Command: duel
# Info: 发起决斗
# Msg: 发起决斗
# Usage: duel <@用户>
# [HELPEND]

async def start_duel(user: User, rival: User):
    scheduler = Scheduler([user, rival], user.user_id)
    await scheduler.start()
    await finish(
        get_currency_key("empty"),
        [
            lang.text("sign.hr", [], user.user_id).join(
                scheduler.logger.logs
            )
        ],
        user.user_id,
    )


@create_command("duel")
async def _(bot: Bot, event: MessageEvent, message: Message) -> None:
    # NOTE 这玩意是一个模拟竞技场，所以除了物品什么的和实际数值不挂钩
    if message[0].type != "at":
        await finish(get_currency_key("unknown_argv"), [message], event.user_id)
    user_id = event.get_user_id()
    user = User(user_id, get_max_hp(event.user_id))
    user.team_id = user_id
    user.set_output(bot, event)
    user.name = event.sender.card or event.sender.nickname or user_id
    rival_id = str(message[0].data["qq"])
    rival = User(rival_id, get_max_hp(message[0].data["qq"]))
    rival.team_id = rival_id
    rival.set_output(bot, event)
    message_id = await send_message(
        bot,
        event,
        "duel.request",
        [MessageSegment.at(rival_id), MessageSegment.at(user_id)],
    )
    matcher = on_message(to_me())
    disposed = False

    @matcher.handle()
    async def _(event: MessageEvent) -> None:
        nonlocal disposed
        if (
            event.reply is None
            or event.reply.message_id != message_id
            or not event.message.extract_plain_text()
            or event.get_user_id() != rival_id
        ):
            await matcher.finish()
        match event.message.extract_plain_text().lower()[0]:
            case "y" | "a":
                disposed = True
                rival.name = (
                    event.sender.card or event.sender.nickname or str(event.user_id)
                )
                matcher.destroy()
                await start_duel(user, rival)
            case "n" | "r":
                disposed = True
                matcher.destroy()
            case _:
                await matcher.finish()

    await asyncio.sleep(90)
    if not disposed:
        await bot.delete_msg(message_id=message_id)
        matcher.destroy()
