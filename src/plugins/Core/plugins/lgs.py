from ._utils import *


@create_command("launch-genshin-impact", {"lgs", "lgi"})
async def _(_bot, event: MessageEvent, _message):
    Json("data/lgs.count.json").add(event.get_user_id(), 1)
    await finish("lgs.launch", [], event.user_id, False, True)


# [HELPSTART] Version: 2
# Command: lgs
# Usage: launch-genshin-impact
# Info: 打开原神
# [HELPEND]
