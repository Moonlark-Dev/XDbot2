import asyncio
from ._utils import *
from .etm.user import get_hp, remove_hp
from .etm.health import get_max_hp
from .etm.duel.entity.user import User
from .help import get_command_start
from nonebot.rule import to_me


async def start_duel(): ...


@create_command("duel")
async def _(bot: Bot, event: MessageEvent, message: Message) -> None:
    if message[-1].type != "at":
        await finish(get_currency_key("unknown_argv"), ["duel"], event.user_id)
    user_id = event.get_user_id()
    user = User(user_id, get_max_hp(event.user_id))
    user.team_id = user_id
    rival_id = str(message[-1].data["qq"])
    rival = User(rival_id, get_max_hp(message[-1].data["qq"]))
    rival.team_id = rival_id
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
            case "n" | "r":
                disposed = True
            case _:
                await matcher.finish()

    await asyncio.sleep(90)
    if not disposed:
        await bot.delete_msg(message_id=message_id)
        matcher.destroy()
