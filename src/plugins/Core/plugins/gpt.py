from nonebot import on_command
from nonebot.adapters.onebot.v11 import Message
from nonebot.matcher import Matcher
from nonebot.params import CommandArg
from steamship import Steamship
import json
import os
import asyncio
import traceback
from . import _error as error

config = json.load(open("data/gpt.config.json", encoding="utf-8"))
os.environ["STEAMSHIP_API_KEY"] = config["api_key"]
client = Steamship(workspace=config["workspace"])
generator = client.use_plugin(config["plugin"])


@on_command("gpt").handle()
async def _(matcher: Matcher, message: Message = CommandArg()):
    try:
        task = generator.generate(text=message.extract_plain_text())
        while task.state in ["waiting", "running"]:
            await asyncio.sleep(config["sleep"])
            task.refresh()
        if task.state == "succeeded":
            await matcher.finish(task.output.blocks[0].text, at_sender=True)
    except:
        await error.report(traceback.format_exc(), matcher)
            
