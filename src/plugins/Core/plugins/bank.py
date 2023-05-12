from nonebot import on_command
import json

CONFIG = json.load(open("data/bank.config.json", encoding="utf-8"))
interest_rate = CONFIG["interest_rate"]
bank_command = on_command("bank")

# [HELPSTART] Version: 2
# Command: bank
# Msg: 银行
# Info: 银行
# Usage: bank
# [HELPEND]
