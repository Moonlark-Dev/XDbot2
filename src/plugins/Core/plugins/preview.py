import re
import traceback
from nonebot.matcher import Matcher
from . import _lang as lang
from nonebot import on_command, on_regex
from nonebot.adapters.onebot.v11 import Message, MessageSegment, MessageEvent
from nonebot.exception import FinishedException
from nonebot.params import CommandArg
from PIL import Image, ImageDraw, ImageFont
from . import _error
from ._utils import *
import os
from playwright.async_api import async_playwright
import time
import asyncio
import os.path

preview = on_command("preview", aliases={"预览网页", "prev"})
latest_time = time.time() - 10
builtin_urls = {
    "six": "http://127.0.0.1:38192/six",
    "ban": "http://127.0.0.1:38192/ban/%group_id%",
    "setu": "http://127.0.0.1:38192/setu",
    "xtbot": "https://xtbot-status.xxtg666.top/?r=5",
}

from urllib.parse import urlparse


def check_url_protocol(url):
    # 使用urlparse解析URL
    parsed_url = urlparse(url)

    # 检查URL是否包含协议部分
    return bool(parsed_url.scheme)


async def take_screenshot_of_website(url: str, matcher: Matcher) -> None:
    file_name = f"preview.image_{int(time.time())}"
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(url)
        await asyncio.sleep(1)  # 等待页面加载完成，参考 Issue#61
        url = page.url
        await page.screenshot(path=f"data/{file_name}.png", full_page=True)
        await browser.close()
    # 处理图片
    image = Image.open(f"data/{file_name}.png")
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    draw.text((0, 0), url, (0, 0, 0), font=font)
    image.save(f"data/{file_name}.png")
    # 发送图片
    await matcher.send(
        Message(
            MessageSegment.image(
                file=f"file://{os.path.abspath(os.path.join('./data', f'{file_name}.png'))}"
            )
        )
    )
    # 删除图片 (Issue #66)
    os.remove(os.path.abspath(os.path.join("./data", f"{file_name}.png")))


# [HELPSTART] Version: 2
# Command: preview
# Usage: preview <url>
# Usage: preview {six|ban|setu}
# Info: 预览XDbot2内置或外部网页
# Msg: 预览网页
# Command: auto-preview
# Usage: auto-preview {on|off}
# Info: 收到 URL 时自动发送网页截图
# Msg: 自动预览
# [HELPEND]


def get_reply_message(event: MessageEvent) -> str:
    if event.reply:
        return event.reply.message.extract_plain_text()
    else:
        return ""


@preview.handle()
async def preview_website(event: MessageEvent, message: Message = CommandArg()):
    global latest_time
    try:
        if time.time() - latest_time < 10:
            await preview.finish(f"冷却中（{10 - time.time() + latest_time}s）")
        latest_time = time.time()
        # 解析参数
        url = str(message) or get_reply_message(event)
        if url in builtin_urls.keys():
            url = builtin_urls[url]
            if "%group_id%" in url:
                try:
                    url = url.replace(
                        "%group_id%", event.get_session_id().split("_")[1]
                    )
                except IndexError:
                    await preview.finish(
                        lang.text("preview.only_group", [], event.get_user_id())
                    )
        if not check_url_protocol(url):
            url = "http://" + url
        # 截取网页
        await take_screenshot_of_website(url, preview)

    except FinishedException:
        raise FinishedException()
    except BaseException:
        await _error.report(traceback.format_exc(), preview)


@create_group_command("auto-preview")
async def _(bot: Bot, event: GroupMessageEvent, message: Message) -> None:
    match message.extract_plain_text().lower():
        case "on" | "enable" | "启用" | "开启":
            Json("preview.auto_groups.json")[str(event.group_id)] = True

        case "off" | "disable" | "禁用" | "关闭":
            Json("preview.auto_groups.json")[str(event.group_id)] = True

        case _:
            Json("preview.auto_groups.json")[str(event.group_id)] = not Json(
                "preview.auto_groups.json"
            )[str(event.group_id)]
    await finish(
        "preview.auto",
        [Json("preview.auto_groups.json")[str(event.group_id)]],
        event.user_id,
    )


@on_regex("(https?|ftp)://[^\s/$.?#].[^\s]*").handle()
async def _(event: GroupMessageEvent, matcher: Matcher = Matcher()) -> None:
    if not Json("preview.auto_groups.json")[str(event.group_id)]:
        return
    if event.get_plaintext()[1:].startswith("preview"):
        return
    match = re.search("(https?|ftp)://[^\s/$.?#].[^\s]*", event.get_plaintext())
    if match is None:
        return
    await take_screenshot_of_website(match.group(0), matcher)
