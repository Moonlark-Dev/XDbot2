import traceback
from nonebot import on_command
import httpx
from nonebot.adapters.onebot.v11 import Message
from nonebot.matcher import Matcher
from nonebot.params import CommandArg
from . import _error as error
import json


config = json.load(open("data/github.config.json", encoding="utf-8"))

def update_config():
    global config
    config = json.load(open("data/github.config.json", encoding="utf-8"))

def save_config():
    json.dump(config, open("data/github.config.json", "w", encoding="utf-8"))
    


@on_command("github", aliases={"gh"}).handle()
async def github(matcher: Matcher, message: Message = CommandArg()):
    try:
        argument = str(message).split(" ")
        if argument[0] == "login":
            if len(argument) == 1:
                await matcher.send(f'请在浏览器打开 https://github.com/login/oauth/authorize?client_id={config["client_id"]}&scope=repo')
        elif argument[0] == "set":
            if argument[1] == "id":
                config["client_id"] = argument[2]
            elif argument[1] == "secret":
                config["secret"] = argument[2]
    except:
        await error.report(traceback.format_exc(), matcher)
