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

# 由于脑子不好在开发过程中把 lend 写成了 lead，懒得重构了，看的时候幸苦下（
# —— This-is-XiaoDeng 2023-05-27

# [HELPSTART] Version: 2
# Command: bank
# Msg: 银行
# Info: XDbot2 银行
# Usage: bank lend <money>：贷款 money vi
# Usage: bank view：查看需还贷金额
# Usage: bank repay <ID>：还贷
# [HELPEND]


def get_max_lead(user_id: str):
    return CONFIG["max_lead"] - user.get_user_data(user_id)["vimcoin"]


def get_leaded_money(user_id: str):
    leaded = 0
    for item in data.bank_lead_data[user_id]:
        leaded += item["money"]
    return leaded


def lead_money(user_id: str, money: int):
    if get_leaded_money(user_id) + money <= get_max_lead(user_id):
        data.bank_lead_data[user_id].append(
            {"money": money, "time": time.time()})
        economy.add_vi(user_id, money)
        return True
    return False


@bank_command.handle()
async def bank(event: MessageEvent, message: Message = CommandArg()):
    try:
        argv = message.extract_plain_text().split(" ")
        user_id = event.get_user_id()
        if user_id not in data.bank_lead_data.keys():
            data.bank_lead_data[user_id] = []

        match argv[0]:
            case "lead" | "lend":
                if lead_money(user_id, max(int(argv[1]), 0)):
                    await bank_command.finish(_lang.text("currency.ok", [], user_id))
                else:
                    await bank_command.finish(_lang.text("bank.full", [
                        get_max_lead(user_id) - get_leaded_money(user_id)], user_id))
            case "view" | "":
                debt_list = ""
                length = 0
                amount_to_be_repaid = 0
                for item in data.bank_lead_data[user_id]:
                    length += 1
                    interest = round(
                        interest_rate * ((time.time() - item["time"]) / 43200) * item["money"], 3)
                    debt_list += _lang.text(
                        "bank.item", [length, item["money"], interest], user_id)
                    amount_to_be_repaid += item["money"] + interest
                await bank_command.finish(_lang.text(
                    "bank.view", [
                        amount_to_be_repaid,
                        debt_list], user_id))
            case "repay":
                debt_info = data.bank_lead_data[user_id][int(argv[1]) - 1]
                interest = round(
                    interest_rate * ((time.time() - debt_info["time"]) / 43200) * debt_info["money"], 3)
                if user.get_user_data(
                        user_id)["vimcoin"] >= debt_info["money"] + interest:
                    economy.use_vimcoin(user_id, debt_info["money"] + interest)
                    data.bank_lead_data[user_id].pop(int(argv[1]) - 1)
                    await bank_command.finish(_lang.text("currency.ok", [], user_id))
                else:
                    await bank_command.finish(_lang.text("currency.no_money", [debt_info["money"] + interest], user_id))

            case _:
                await bank_command.finish(_lang.text("bank.usage", [], user_id))
    except BaseException:
        await _error.report(traceback.format_exc(), bank_command)
