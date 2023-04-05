import traceback
from nonebot import on_command
import httpx
from nonebot.adapters.onebot.v11 import Message
from nonebot.matcher import Matcher
from nonebot.log import logger
from nonebot.params import CommandArg
from . import _error as error
import json
import urllib.parse


config = json.load(open("data/github.config.json", encoding="utf-8"))

def update_config():
    global config
    config = json.load(open("data/github.config.json", encoding="utf-8"))

def save_config():
    json.dump(config, open("data/github.config.json", "w", encoding="utf-8"))
    
def get_headers():
    return {
        "Authorization": f"Bearer {config['access_token']}"
    }

def get_proxy():
    try:
        return config["proxies"]
    except:
        return None


@on_command("github", aliases={"gh"}).handle()
async def github(matcher: Matcher, message: Message = CommandArg()):
    try:
        argument = str(message).split(" ")
        if argument[0] == "login":
            if len(argument) == 1:
                await matcher.send(f'请在浏览器打开 https://github.com/login/oauth/authorize?client_id={config["client_id"]}&scope=repo')
            else:
                code = argument[1]
                async with httpx.AsyncClient(proxies=get_proxy()) as client:
                    response = await client.get(
                            f"https://github.com/login/oauth/access_token?client_id={config['client_id']}&client_secret={config['secret']}&code={code}")
                content = response.read().decode("utf-8")
                logger.debug(content)
                config["access_token"] = urllib.parse.parse_qs(content)["access_token"][0]
                save_config()
                async with httpx.AsyncClient(proxies=get_proxy()) as client:
                    response = await client.get(
                        "https://api.github.com/user",
                        headers=get_headers())
                await matcher.finish(f"已成功登录到 {json.loads(response.read())['login']}")
                

        elif argument[0] == "set":
            if argument[1] == "id":
                config["client_id"] = argument[2]
                await matcher.send("ClientID 已设置")
            elif argument[1] == "secret":
                config["secret"] = argument[2]
                await matcher.send("Secret 已设置")
            elif argument[1] == "proxies":
                config["proxies"] = argument[2]
            save_config()
    except:
        await error.report(traceback.format_exc(), matcher)
