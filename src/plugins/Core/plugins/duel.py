import asyncio
from ._utils import *
from .etm.user import get_hp, remove_hp
from .etm.health import get_max_hp
from .etm.duel.entity.user import User
from .help import get_command_start
from nonebot.rule import to_me
from .etm.duel.scheduler import Scheduler


async def start_duel(user: User, rival: User):
    scheduler = Scheduler(
        [user, rival],
        user.user_id
    )
    await scheduler.start()
    await finish(get_currency_key("empty"), [
        "\n-\n".join(scheduler.logger.logs + [scheduler.logger.current, str(user.hp), str(rival.hp),str(user.max_hp), str(scheduler.is_finished())])
    ], user.user_id)


@create_command("duel")
async def _(bot: Bot, event: MessageEvent, message: Message) -> None:
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
                rival.name = event.sender.card or event.sender.nickname or str(event.user_id)
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
