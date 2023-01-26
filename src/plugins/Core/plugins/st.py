from nonebot import on_command
from . import _error
import nonebot.adapters.onebot.v11.message
import nonebot.adapters.onebot.v11
import random
import traceback

st = on_command("st", aliases={"随机图片"})
api_list = [
    "https://img.xjh.me/random_img.php?return=302",
    "https://api.vvhan.com/api/acgimg",
    "https://api.yimian.xyz/img?type=moe",
    "https://api.yimian.xyz/img?type=wallpaper",    # <- 偷偷混进去的Bing壁纸API
    "https://api.yimian.xyz/img?type=head"
]


@st.handle()
async def st_handle():
    try:
        await st.finish(
            nonebot.adapters.onebot.v11.message.Message(
                nonebot.adapters.onebot.v11.MessageSegment.image(
                    random.choice(api_list))))
    except Exception:
        await _error.report(traceback.format_exc(), st)
