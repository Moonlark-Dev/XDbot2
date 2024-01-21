from .etm import bag
from ._utils import *
from .etm import merger


@create_command("bag-tidy", {"bag-clean"})
async def _(bot: Bot, event: MessageEvent, message: Message) -> None:
    user_id = event.get_user_id()
    bag.bags[user_id] = merger.merge_item_list(bag.bags[user_id])
    await finish(get_currency_key("ok"), [], user_id)

# [HELPSTART] Version: 2
# Command: bag-tidy
# Msg: 整理背包
# Info: 整理背包
# Usage: bag-tidy
# [HELPEND]
