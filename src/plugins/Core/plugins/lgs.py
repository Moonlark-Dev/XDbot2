from ._utils import *


@create_command("launch-genshin-impact", {"lgs", "lgi"})
async def _(_bot, event: MessageEvent, message: Message):
    if message.extract_plain_text().strip() == "status":
        await finish(
            "lgs.status",
            [Json("data/lgs.count.json")[event.get_user_id()]],
            event.user_id
        )
    Json("data/lgs.count.json").add(event.get_user_id(), 1)
    await finish("lgs.launch", [], event.user_id, False, True)


# [HELPSTART] Version: 2
# Command: lgs
# Usage: launch-genshin-impact：启动原神
# Usage: lgs status：查看原神启动次数
# Info: 打开原神
# [HELPEND]
