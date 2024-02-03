from ._utils import *

# [HELPSTART] Version: 2
# Command: gpt-config
# Usage: gpt-config 16k：启用/禁用 16k 模型（建议 Plus 开启）
# Usage: gpt-config auto-pay：启用/禁用在 TOKEN 不足时自动支付
# Msg: GPT设置
# Info: XDbot2 GPT 设置
# [HELPEND]

@create_command("gpt-config")
async def _(bot: Bot, event: MessageEvent, message: Message) -> None:
    argv = message.extract_plain_text().split(" ")
    user_id = event.user_id
    match argv[0]:
        case "16k":
            await set_switch(
                f"gpt/users/{user_id}.json",
                "16k",
                get_list_item(argv, 1, ""),
                user_id
            )
        case "auto-pay":
            await set_switch(
                f"gpt/users/{user_id}.json",
                "automatic_payment",
                get_list_item(argv, 1, ""),
                user_id
            )
        case _:
            await finish(get_currency_key("wrong_argv"), ["gpt-config"], event.user_id)