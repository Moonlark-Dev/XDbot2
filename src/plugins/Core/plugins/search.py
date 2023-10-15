from ._utils import *
from nonebot.adapters.onebot.v11.message import MessageSegment
from playwright.async_api import async_playwright
import asyncio
import time


# [HELPSTART] Version: 2
# Command: search
# Info: 在 Bing 上搜索
# Msg: 必应搜索
# Usage: search <content>
# [HELPEND]

@create_command("search", aliases={"bing"})
async def handle_search_command(bot: Bot, event: MessageEvent, message: Message, matcher: Matcher = Matcher()):
    url = "https://www.bing.com/search?q=" + message.extract_plain_text().replace(" ", "+")
    file_name = f"preview.image_{int(time.time())}.ro"
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(url)
        await asyncio.sleep(5)  
        url = page.url
        await page.screenshot(path=f"data/{file_name}.png", full_page=True)
        await browser.close()
    await matcher.send(Message(
        MessageSegment.image(
            file=f"file://{os.path.abspath(os.path.join('./data', f'{file_name}.png'))}"
        )
    ))
