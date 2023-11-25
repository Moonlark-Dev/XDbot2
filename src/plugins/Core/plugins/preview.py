import traceback
from . import _lang as lang
from nonebot import on_command
from nonebot.adapters.onebot.v11 import Message, MessageSegment, MessageEvent
from nonebot.exception import FinishedException
from nonebot.params import CommandArg
from PIL import Image, ImageDraw, ImageFont
from . import _error
import os
from playwright.async_api import async_playwright
import time
import asyncio
import os.path

preview = on_command("preview", aliases={"预览网页"})
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


# [HELPSTART] Version: 2
# Command: preview
# Usage: preview <url>
# Usage: preview {six|ban|setu}
# Info: 预览XDbot2内置或外部网页
# Msg: 预览网页
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
        await preview.send(
            Message(
                MessageSegment.image(
                    file=f"file://{os.path.abspath(os.path.join('./data', f'{file_name}.png'))}"
                )
            )
        )
        # 删除图片 (Issue #66)
        os.remove(os.path.abspath(os.path.join("./data", f"{file_name}.png")))

    except FinishedException:
        raise FinishedException()
    except BaseException:
        await _error.report(traceback.format_exc(), preview)
