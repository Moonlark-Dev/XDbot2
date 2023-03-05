import random
from nonebot.exception import FinishedException
from nonebot import on_command
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Bot, MessageEvent
from nonebot.adapters.onebot.v11.message import Message
from . import _error as error
from . import _lang as lang
import traceback

random_plugin = on_command('random')

# [HELPSTART] Version: 2
# Command: random
# Usage: random
# Usage: random <end>
# Usage: random <start> <end>
# Msg: 在<start>与<end>之间随机取整数，如果不传入参数，则返回0到1的随机小数；如果只传入<end>参数，则从0~<end>随机取数
# Info: 取随机数
# [HELPEND]

@random_plugin.handle()
async def random_handle(event: MessageEvent, message: Message = CommandArg()):
    try:
        # 获取参数
        args = str(message).strip()
        if not args:
            # 如果没有参数，默认返回0到1的随机小数
            result = random.random()
        else:
            # 如果有参数，按照空格拆分，第一个参数为随机数范围的下限，第二个参数为随机数范围的上限
            arg_list = args.split()
            if len(arg_list) == 1:
                result = random.randint(0, int(arg_list[0]))
            elif len(arg_list) == 2:
                result = random.randint(int(arg_list[0]), int(arg_list[1]))
            else:
                # 参数错误
                await random_plugin.finish(lang.text("random_number.argerr", [], event.get_user_id()))
        # 返回结果
        await random_plugin.finish(str(result))
    except FinishedException:
        raise FinishedException()
    except BaseException:
        await error.report(traceback.format_exc(), random_plugin)
