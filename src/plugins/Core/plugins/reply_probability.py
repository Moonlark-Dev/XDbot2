from ._utils import *
from nonebot.permission import SuperUser


@create_command("reply-probability", {"reply-prob"})
async def _(bot: Bot, event: MessageEvent, message: Message) -> None:
    argv = message.extract_plain_text().split(" ")
    match argv[0]:
        case "group-probability" | "group":
            group_id = str(await get_group_id(event))
            if len(argv) == 1:
                await finish("reply_probability.group_info", [Json("reply/config/group_probability.json").get(group_id, 1)], event.user_id)
            elif event.sender.role not in ["owner", "admin"] or event.get_user_id() not in bot.config.superusers:
                await finish("reply_probability.403", [], event.user_id)
            Json("reply/config/group_probability.json")[group_id] = float(argv[1])
            await finish(get_currency_key("ok"), [], event.user_id)
        case "":
            await finish("reply_probability.info", [Json("reply/config/probability.json").get(event.get_user_id(), 1)], event.user_id)
        case _:
            Json("reply/config/probability.json")[event.get_user_id()] = float(argv[0])
            await finish(get_currency_key("ok"), [], event.user_id)

# [HELPSTART] Version: 2
# Command: reply-prob
# Msg: 调教触发概率
# Info: 调整调教触发概率（概率参数均为小数，<=1，为 0 为关闭）
# Usage: reply-prob group <概率>：调整当前群聊的触发概率
# Usage: reply-prob <概率>：调整对自己的触发概率
# Usage: reply-prob group：查看当前群聊的触发概率
# Usage: reply-prob：查看对自己的触发概率
# [HELPEND]
