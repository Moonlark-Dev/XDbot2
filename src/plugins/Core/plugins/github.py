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
from . import _lang
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


async def get_repo_info(matcher: Matcher, event: MessageEvent):
    repo = re.search(
            r"[a-zA-Z0-9_-]+/[a-zA-Z0-9_-]+",
            event.get_plaintext().replace("github.com", ""))[0]
    repo_data = await call_github_api(f"https://api.github.com/repos/{repo}")
    # 发送
    await matcher.send(_lang.text("github.repo_info", [
        repo_data['html_url'],
        repo_data['full_name'],

        _lang.text(
            "github.repo_archived",
            [],
            event.get_user_id()
        ) if repo_data['archived'] else "",

        repo_data['owner']['login'],
        repo_data['stargazers_count'],
        repo_data['open_issues'],
        
        len(await call_github_api(
            repo_data['pulls_url'].replace("{/number}", ""))),
        
        repo_data['watchers'],
        repo_data['forks'],
        repo_data['language'],
        repo_data['license']['name'],
        repo_data["created_at"],
        repo_data['updated_at'],
        repo_data['description']], event.get_user_id()))

# [HELPSTART] Version: 2
# Command: github
# Msg: GitHub解析
# Usage: gh login
# Usage: gh login <code>
# Usage: gh set {client_id|secret|proxies} <值>
# Usage: gh <owner>/<repo>

@on_command("github", aliases={"gh"}).handle()
async def github(matcher: Matcher, event: MessageEvent, message: Message = CommandArg()):
    try:
        argument = str(message).split(" ")
        if argument[0] == "login":
            if len(argument) == 1:
                await matcher.send(_lang.text("github.open_url", [config["client_id"]], event.get_user_id()))
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
                await matcher.finish(_lang.text("github.login_successful", [(await call_github_api('https://api.github.com/user'))['login']], event.get_user_id()))
        elif argument[0] == "set":
            if argument[1] == "client_id":
                config["client_id"] = argument[2]
                await matcher.send(_lang.text("currency.ok", [], event.get_user_id()))
            elif argument[1] == "secret":
                config["secret"] = argument[2]
                await matcher.send(_lang.text("currency.ok", [], event.get_user_id()))
            elif argument[1] == "proxies":
                config["proxies"] = argument[2]
                await matcher.send(_lang.text("currency.ok", [], event.get_user_id()))
            else:
                await matcher.finish(_lang.text("currency.unknown_argv", [argument[1]], event.get_user_id()))
            save_config()
        else:
            await get_repo_info(matcher, event)
        
    except BaseException:
        await error.report(traceback.format_exc(), matcher)


@on_regex(r"(github\.com/[a-zA-Z0-9_-]+/[a-zA-Z0-9_-]+/issues/[0-9]+)").handle()
async def get_issue(matcher: Matcher, event: MessageEvent):
    try:
        repo, issue_id = re.search(
            r"[a-zA-Z0-9_-]+/[a-zA-Z0-9_-]+/issues/[0-9]+",
            event.get_plaintext().replace("github.com", ""))[0].split("/issues/")
        issue_data = await call_github_api(f"https://api.github.com/repos/{repo}/issues/{issue_id}")
        labels = ""
        for label in issue_data["labels"]:
            labels += f"{label['name']}, "
        await matcher.finish(_lang.text("github.issue_info", [
            issue_data['html_url'],
            issue_data['title'],
            issue_data['state'],
            issue_data['user']['login'],
            issue_data['created_at'],
            labels[:-2],
            issue_data['body']], event.get_user_id()))

    except BaseException:
        await error.report(traceback.format_exc(), matcher)


@on_regex(r"(github\.com/[a-zA-Z0-9_-]+/[a-zA-Z0-9_-]+/pull/[0-9]+)").handle()
async def get_pull(matcher: Matcher, event: MessageEvent):
    try:
        repo, pull_id = re.search(r"[a-zA-Z0-9_-]+/[a-zA-Z0-9_-]+/pull/[0-9]+",
                                  event.get_plaintext().replace("github.com", ""))[0].split("/pull/")
        pull_data = await call_github_api(f"https://api.github.com/repos/{repo}/pulls/{pull_id}")
        await matcher.finish(_lang.text("github.pr_info", [
            pull_data['html_url'],
            pull_data['title'],
            pull_data['state'],
            pull_data['user']['login'],
            pull_data['updated_at'],
            pull_data['body']], event.get_user_id()))

    except BaseException:
        await error.report(traceback.format_exc(), matcher)


@on_regex(r"(github\.com/[a-zA-Z0-9_-]+/[a-zA-Z0-9_-]+)|(^[a-zA-Z0-9_-]+/[a-zA-Z0-9_-]+)").handle()
async def get_repo(matcher: Matcher, event: MessageEvent):
    try:
        if ("pull" in event.get_plaintext().split("/") or
                "issues" in event.get_plaintext().split("/")):
            await matcher.finish()
        try:
            get_repo_info(matcher, event)
        except BaseException:
            pass
        # 删除缓存
        # os.remove(file)

    except BaseException:
        await error.report(traceback.format_exc(), matcher)
