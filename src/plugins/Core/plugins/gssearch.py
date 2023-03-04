import requests
from nonebot import on_command
from nonebot.adapters.onebot.v11 import GroupMessageEvent
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11.message import Message, MessageSegment
import asyncio
from nonebot.adapters.onebot.v11.bot import Bot as bot

gssearch = on_command("gssearch", aliases={"原神角色查询", "西风驿站"}, priority=10)


@gssearch.handle()
async def handle_first_receive(event: GroupMessageEvent, bot: bot, message: Message = CommandArg()):

    #蒙德(done)

    if str(message) == "风主":
        pic = MessageSegment.image(requests.get("https://upload-bbs.miyoushe.com/upload/2022/05/20/74019947/374c90a6ef78d74888e797c1b6624723_3616634552285922830.png").content)
    elif str(message) == "安柏":
        pic = MessageSegment.image(requests.get("https://upload-bbs.miyoushe.com/upload/2022/05/06/74019947/d2c1e47d8a6208cba75818903e8ba69c_259281589678097536.png").content)
    elif str(message) == "凯亚":
        pic = MessageSegment.image(requests.get("https://upload-bbs.miyoushe.com/upload/2022/05/06/74019947/27bee1b397be78832ae44b28e00d3e5f_8387119502215650487.png").content)
    elif str(message) == "丽莎":
        pic = MessageSegment.image(requests.get("https://upload-bbs.miyoushe.com/upload/2022/05/07/74019947/342e8cb47732f9a5bd95ad6b9e649cd7_4781190622259563758.png").content)
    elif str(message) == "芭芭拉":
        pic = MessageSegment.image(requests.get("https://upload-bbs.miyoushe.com/upload/2022/05/04/74019947/8e5b11dceb189bafc2d5cd03157c7d18_7888032257811020437.png").content)
    elif str(message) == "琴":
        pic = MessageSegment.image(requests.get("https://upload-bbs.miyoushe.com/upload/2022/04/17/74019947/ecb13996746f44ad2939f70aebd3ee5c_4319548421481258646.png").content)
    elif str(message) == "迪卢克":
        pic = MessageSegment.image(requests.get("https://upload-bbs.miyoushe.com/upload/2022/04/12/74019947/041cd75cf2fe7dfb107009ed0c4d7908_3686953124385499396.png").content)
    elif str(message) == "雷泽":
        pic = MessageSegment.image(requests.get("https://upload-bbs.miyoushe.com/upload/2022/04/21/74019947/edd6734d73b2c3a1bbce352e326cca33_6347727738945370608.png").content)
    elif str(message) == "阿贝多":
        pic = MessageSegment.image(requests.get("https://upload-bbs.miyoushe.com/upload/2022/04/30/74019947/5f04d36fa29e6d52334f6df88e3de8f3_1265129183994784076.png").content)
    elif str(message) == "可莉":
        pic = MessageSegment.image(requests.get("https://upload-bbs.miyoushe.com/upload/2022/04/22/74019947/a51855b207edba6751ec1beb2f7df305_4046038425893957924.png").content)
    elif str(message) == "温迪":
        pic = MessageSegment.image(requests.get("https://upload-bbs.miyoushe.com/upload/2022/03/26/74019947/67955823ca97f5d578b62d7489544bce_1343760092805173875.png").content)
    elif str(message) == "班尼特":
        pic = MessageSegment.image(requests.get("https://upload-bbs.miyoushe.com/upload/2022/04/05/74019947/deb7c21f15957f9ea54c4c59d51384c5_6524333797006182492.png").content)
    elif str(message) == "迪奥娜":
        pic = MessageSegment.image(requests.get("https://upload-bbs.miyoushe.com/upload/2022/04/24/74019947/369cf8b57758d2a3dc1c201208c94a62_4290873316135656553.png\").content)
    elif str(message) == "莫娜":
        pic = MessageSegment.image(requests.get("https://upload-bbs.miyoushe.com/upload/2022/04/18/74019947/e45b3662d49485ad45d1c15c86ee8ff1_6147281555794418997.png").content)
    elif str(message) == "诺艾尔":
        pic = MessageSegment.image(requests.get("https://upload-bbs.miyoushe.com/upload/2022/04/19/74019947/66aff13e464a8d356cdcc2770e8d561a_77951686589137205.png").content)
    elif str(message) == "优菈":
        pic = MessageSegment.image(requests.get("https://upload-bbs.miyoushe.com/upload/2022/04/26/74019947/6956c7dd416a18aa2f3d01d31b224c7f_6881120949080868609.png").content)
    elif str(message) == "罗莎莉亚":
        pic = MessageSegment.image(requests.get("https://upload-bbs.miyoushe.com/upload/2022/04/20/74019947/cb23ecdf67076903655f04828b22ac1e_9052213692875242731.png").content)
    elif str(message) == "埃洛伊":
        pic = MessageSegment.image(requests.get("https://upload-bbs.miyoushe.com/upload/2022/04/24/74019947/2540c26a2ac2577b3167f53db3c52dbc_1799590105380907974.png").content)
    elif str(message) == "砂糖":
        pic = MessageSegment.image(requests.get("https://upload-bbs.miyoushe.com/upload/2022/04/21/74019947/572601cc24092a0b6eaee8906cb87bcf_8296508453075717975.png").content)
    elif str(message) == "菲谢尔":
        pic = MessageSegment.image(requests.get("https://upload-bbs.miyoushe.com/upload/2022/04/28/74019947/e58ddfb05f1b892c6a5b4f13c54778f8_8036909337049568299.png").content)

    #璃月(todo)

    #稻妻(todo)

    #须弥(todo)

    else:
        await gssearch.finish(f"未找到"+message)
    msgb = pic + f"攻略制作:猫冬 https://www.miyoushe.com/ys/accountCenter/postList?id=74019947"
    msg = await vocaloid.send(msgb)
    await asyncio.sleep(114)
    await bot.delete_msg(message_id=msg['message_id'])
    await vocaloid.finish(f" ")
    
# [HELPSTART]
# !Usage gssearch gssearch <角色名>
# !Info gssearch 查询角色攻略
# [HELPEND]
