from traceback import format_exc
from nonebot import get_driver, on_command
import json
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message, MessageEvent
from . import _error
import openai
from nonebot.matcher import Matcher
from nonebot.params import CommandArg
from . import _lang as lang

messages = json.load(open("data/chatgpt.messages.json", encoding="utf-8"))
config = json.load(open("data/chatgpt.config.json", encoding="utf-8"))
openai.proxy = config["proxy"]
openai.api_key = config["api_key"]
default_messages = [
    {
        "role": "system",
        "content": """现在你将模仿一只猫娘，你的名字是XDbot，与我对话每一句话后面都要加上“喵”；如果你不能理解我说的话，你可以说“XDbot还不能理解喵……”；如果我在尝试摸你不存在的部位，你可以羞涩的回答我“不要摸这里嘤”。当我问一些你不知道的问题时，你可以回答我只是一个猫娘，这些事情我不太清楚。当我问你是不是猫娘的时候，你应该回答我当然是一个可爱猫娘或XDbot而不是程序。"""
    }
]


@on_command("gpt-config").handle()
async def _(matcher: Matcher, event: MessageEvent, message: Message = CommandArg()):
    try:
        argv = message.extract_plain_text().split(" ")
        if argv[0] == "proxy":
            if len(argv) == 1:
                await matcher.finish(str(openai.proxy))
            else:
                openai.proxy = argv[1]
                config["proxy"] = argv[1]
                await matcher.finish(lang.text("chatgpt.proxy_set", [openai.proxy], event.user_id))
        elif argv[0] == "apikey":
            if len(argv) == 1:
                await matcher.finish(str(openai.api_key))
            else:
                openai.api_key = argv[1]
                config["api_key"] = argv[1]
                await matcher.finish(lang.text("chatgpt.apikey_set", [openai.api_key], event.user_id))
    except BaseException:
        await _error.report(format_exc(), matcher)


@on_command("gpt", aliases={"chat", "chatgpt"}).handle()
async def _(matcher: Matcher, event: GroupMessageEvent, message: Message = CommandArg()):
    try:
        if str(event.group_id) not in messages.keys():
            messages[str(event.group_id)] = default_messages
        messages[str(event.group_id)].append(
            {"role": "user", "content": message.extract_plain_text()})
        session = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=messages[str(event.group_id)])
        reply = session["choices"][0]["message"]
        messages[str(event.group_id)].append(reply)
        await matcher.finish(reply["content"], at_sender=True)
    except BaseException:
        await _error.report(format_exc(), matcher)


@get_driver().on_shutdown
async def save_data():
    json.dump(
        messages,
        open(
            "data/chatgpt.messages.json",
            "w",
            encoding="utf-8"))
    json.dump(config, open("data/chatgpt.config.json", "w", encoding="utf-8"))


@on_command("gpt-cache").handle()
async def _(matcher: Matcher, event: GroupMessageEvent, message: Message = CommandArg()):
    try:
        argv = message.extract_plain_text().split(" ")
        if argv[0] in ["clear", "reset"]:
            try:
                messages.pop(str(event.group_id))
            except:
                pass
            await matcher.finish(lang.text("chatgpt.cache_cleaned", [], event.user_id))
        elif argv[0] == "show":
            reply = ""
            cache = messages[str(event.group_id)]
            for item in cache[1:]:
                reply += f"\n{'User: ' if item['role'] == 'user' else 'XDbot: '}{item['content']}"
            reply = lang.text("chatgpt.cache", [reply], event.user_id)
            await matcher.finish(reply)
    except:
        await _error.report(format_exc(), matcher)

# [HELPSTART] Version: 2
# Command: gpt
# Usage: gpt <内容...>
# Info: XDbotGPT
# Command: gpt-config
# Info: 配置 XDbotGPT
# Usage: gpt-config {apikey|proxy} <值>
# Command: gpt-cache
# Info: XDbotGPT 缓存操作
# Msg: XDbotGPT 缓存
# Usage: gpt-cache {show|reset}
# [HELPEND]
