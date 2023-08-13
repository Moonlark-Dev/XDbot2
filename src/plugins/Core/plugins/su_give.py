from .su import su
from . import _error
from nonebot.adapters import Message
from nonebot.params import CommandArg
from .etm import bag

try:
    import json5 as json
except:
    import json


@su.handle()
async def _(message: Message = CommandArg()):
    try:
        args = str(message).strip().split(" ")
        if args[0] in ["give", "给"]:
            bag.add_item(
                args[1].replace("[CQ:at,qq=", "").replace("]", ""),
                args[2],
                int(args[3]) if len(args) >= 4 and args[3][0] != "{" else 1,
                json.loads(" ".join(args[4:]) if len(args) >= 5 else "{}"),
            )
            await su.finish("完成！")
    except:
        await _error.report()
