from nonebot.adapters.onebot.v11 import MessageEvent
from nonebot.adapters.onebot.v11 import Message
from nonebot.params import CommandArg
from . import _error
from .etm import economy, data, user
from . import _lang
import time
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

def get_leaded_money(user_id: str):
    leaded = 0
    for item in data.bank_lead_data[user_id]:
        leaded += item["money"]
    return leaded

def lead_money(user_id: str, money: int):
    if get_leaded_money(user_id) + money <= get_max_lead:
        data.bank_lead_data[user_id].append({"money": money, "time": time.time()})
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
                    await bank_command.finish(_lang.text("currency.ok", [], user_id))
                else:
                    await bank_command.finish(_lang.text("bank.full", [get_max_lead(user_id) - get_leaded_money(user_id)], user_id))
            case "view":
                pass
            case "repay":
                pass
            case _:
                await bank_command.finish(_lang.text("bank.usage", [], user_id))
    except:
        await _error.report(traceback.format_exc(), bank_command)
