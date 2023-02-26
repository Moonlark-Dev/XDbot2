import traceback
from nonebot import on_command
from nonebot.adapters.onebot.v11 import Message, MessageSegment
from nonebot.exception import FinishedException
from nonebot.params import CommandArg
from PIL import Image, ImageDraw, ImageFont
from . import _error
from playwright.async_api import async_playwright
import time
import os.path

preview = on_command("preview", aliases={"预览网页"})
latest_time = time.time()


@preview.handle()
async def preview_website(message: Message = CommandArg()):
    global latest_time
    try:
        if time.time() - latest_time < 15:
            await preview.finish(f"冷却中（{15 - time.time() + latest_time}s）")
        latest_time = time.time()
        # 截取网页
        file_name = f"preview.image_{int(time.time())}"
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await page.goto(str(message))
            url = page.url
            await page.screenshot(path=f"data/{file_name}.png", full_page=True)
            await browser.close()
        # 处理图片
        image = Image.open(f"data/{file_name}.png")
        draw = ImageDraw.Draw(image)
        font = ImageFont.load_default()
        draw.text((0, 0), url, font=font)
        image.save(f"data/{file_name}.png")
        # 发送图片
        await preview.finish(Message(MessageSegment.image(
            file=f"file://{os.path.abspath(os.path.join('./data', f'{file_name}.png'))}")))

    except FinishedException:
        raise FinishedException()
    except BaseException:
        await _error.report(traceback.format_exc(), preview)
