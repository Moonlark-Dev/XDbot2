from nonebot.adapters.onebot.v11 import MessageEvent
from nonebot.adapters.onebot.v11 import Message
from nonebot.params import CommandArg
from . import _error
from .etm import economy, data, user
from . import _lang
from nonebot import on_command
import json
import traceback

CONFIG = json.load(open("data/bank.config.json", encoding="utf-8"))
interest_rate = CONFIG["interest_rate"]
bank_command = on_command("bank")

# [HELPSTART] Version: 2
# Command: bank
# Msg: 银行
# Info: XDbot2 银行
# Usage: bank lend [money]：贷款 money vi
# Usage: bank view：查看需还贷金额
# Usage: bank repay [money]：还贷
# [HELPEND]

def get_max_lead(user_id: str):
    return CONFIG["max_lead"] - user.get_user_data(user_id)["vimcoin"]

def lead_money(user_id: str, money: int):
    leaded_money = data.bank_leaded.get(user_id) or 0
    if leaded_money + money <= get_max_lead(user_id):
        data.bank_leaded[user_id] = leaded_money + money
        economy.add_vi(user_id, money)
        return True
    return False

@bank_command.handle()
async def bank(event: MessageEvent, message: Message = CommandArg()):
    try:
        argv = message.extract_plain_text().split(" ")
        user_id = event.get_user_id()
        if len(argv) == 0:
            await bank_command.finish(_lang.text("bank.usage", [], user_id))
        match argv[0]:
            case "lend":
                if lead_money(user_id, int(argv[1])):
                    pass
            case "view":
                pass
            case "repay":
                pass
            case _:
                await bank_command.finish(_lang.text("bank.usage", [], user_id))
    except:
        await _error.report(traceback.format_exc(), bank_command)
