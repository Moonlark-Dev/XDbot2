import traceback
from nonebot import on_command, on_regex
import httpx
from nonebot.adapters.onebot.v11 import Message, MessageEvent
import time
# import cairosvg
from nonebot.matcher import Matcher
from nonebot.log import logger
from nonebot.params import CommandArg
from . import _error as error
import json
import urllib.parse
import re
# import os
# import os.path


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


async def call_github_api(url):
    async with httpx.AsyncClient(proxies=get_proxy()) as client:
        response = await client.get(
            url, headers=get_headers())
    logger.debug(response.status_code)
    content = response.read()
    logger.debug(content)
    return json.loads(content)


def get_proxy():
    try:
        return config["proxies"]
    except BaseException:
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
                config["access_token"] = urllib.parse.parse_qs(content)[
                    "access_token"][0]
                save_config()
                await matcher.finish(f"已成功登录到 {(await call_github_api('https://api.github.com/user'))['login']}")
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
    except BaseException:
        await error.report(traceback.format_exc(), matcher)

@on_regex(r"(github\.com/[a-zA-Z0-9_-]+/[a-zA-Z0-9_-]+/pull/[0-9]+)").handle()
async def get_pull(matcher: Matcher, event: MessageEvent):
    try:
        repo, pull_id = re.search(r"[a-zA-Z0-9_-]+/[a-zA-Z0-9_-]+/pull/[0-9]+", event.get_plaintext().replace("github.com", ""))[0].split("/pull")
        pull_data = await call_github_api(f"https://api.github.com/repos/{repo}/pulls/{pull_id}")
        await matcher.finish(f"""{pull_data['html_url']}
标题：{pull_data['title']} ({pull_data['state']})
仓库：{pull_data['head']['repo']['full_name']}
创建者：{pull_data['user']['login']}
创建时间：{pull_data['created_at']}
最后更新：{pull_data['updated_at']}
{pull_data['body']}""")

    except:
        await error.report(traceback.format_exc(), matcher)

@on_regex(r"(github\.com/[a-zA-Z0-9_-]+/[a-zA-Z0-9_-]+)|(^[a-zA-Z0-9_-]+/[a-zA-Z0-9_-]+)").handle()
async def get_repo(matcher: Matcher, event: MessageEvent):
    try:
        repo = re.search(
            r"[a-zA-Z0-9_-]+/[a-zA-Z0-9_-]+",
            event.get_plaintext().replace("github.com", ""))[0]
        repo_data = await call_github_api(f"https://api.github.com/repos/{repo}")
        # 发送
        await matcher.send(Message(f"""{repo_data['html_url']}
全名：{repo_data['full_name']} {"(只读)" if repo_data['archived'] else ""}
所有者：{repo_data['owner']['login']}
星标：{repo_data['stargazers_count']} | 议题：{repo_data['open_issues']} | 拉取请求：{len(await call_github_api(repo_data['pulls_url'].replace("{/number}", "")))}
查看：{repo_data['watchers']} | 复刻：{repo_data['forks']} | 语言：{repo_data['language']}
许可证：{repo_data['license']['name']}
创建日期：{repo_data["created_at"]}
更新日期：{repo_data['updated_at']}
简介：{repo_data['description']}"""))
        # 删除缓存
        # os.remove(file)

    except BaseException:
        await error.report(traceback.format_exc(), matcher)
