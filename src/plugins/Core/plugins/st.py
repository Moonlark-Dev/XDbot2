from nonebot import on_command
from . import _error
from nonebot.adapters.onebot.v11 import MessageSegment
import random
import traceback
from nonebot.exception import FinishedException

st = on_command("st", aliases={"随机图片"})
api_list = [
    "https://img.xjh.me/random_img.php?return=302",
    "https://api.vvhan.com/api/acgimg",
    "https://api.yimian.xyz/img?type=moe",
    "https://api.yimian.xyz/img?type=wallpaper",  # <- 偷偷混进去的Bing壁纸API
    "https://cdn.seovx.com/d/?mom=302",
    "https://img.xjh.me/random_img.php",
    "http://api.btstu.cn/sjbz/?lx=dongman",
    "http://www.dmoe.cc/random.php",
    # "https://api.yimian.xyz/img?type=head"
]


@st.handle()
async def st_handle():
    try:
        await st.finish(MessageSegment.image(random.choice(api_list)))
    except FinishedException:
        raise FinishedException()
    except Exception:
        await _error.report(traceback.format_exc(), st)


# [HELPSTART] Version: 2
# Command: st
# Info: 随机图片
# Usage: st
# [HELPEND]
