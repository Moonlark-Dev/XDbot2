import json
import traceback

from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, Message
from nonebot.exception import FinishedException
from nonebot.params import CommandArg

from . import _userCtrl

bag = on_command("bag", aliases={"背包"})
ctrlGroup = json.load(open("data/ctrl.json", encoding="utf-8"))["control"]


@bag.handle()
async def bagHandle(
        bot: Bot,
        event: GroupMessageEvent,
        message: Message = CommandArg()):
    try:
        argument = message.extract_plain_text().split(" ")
        bagData = json.load(open("data/etm.bag.json", encoding="utf-8"))
        itemData = json.load(open("data/etm.items.json", encoding="utf-8"))
        if argument[0] == "":
            text = f"「{(await bot.get_stranger_info(user_id=event.get_user_id()))['nickname']}的背包」\n"
            length = 0
            for item in bagData[event.get_user_id()]:
                name = item["data"]["displayName"] or itemData[item["id"]]["name"]
                text += f" {length}. {name} x{item['count']}\n"
                length += 1
            await bag.finish(text)
        elif argument[0] == "view" or argument[0] == "查看":
            item = bagData[event.get_user_id()][int(argument[1])]
            name = item["data"]["displayName"] or itemData[item["id"]]["name"]
            info = item["data"]["information"] or itemData[item["id"]]["info"]
            await bag.finish(f"""「{name}」
当前拥有：{item['count']}
{info}
\t
{item['data']}""")
        elif argument[0] == "drop" or argument[0] == "丢弃":
            try:
                _userCtrl.removeItemsFromBag(
                    userID=event.get_user_id(),
                    itemPos=int(argument[1]),
                    count=bagData[event.get_user_id()][int(
                        argument[1])]["count"],
                    removeType="Drop"
                )
            except _userCtrl.ItemCanNotRemove:
                await bag.finish("物品被标记为：无法丢弃")
            await bag.finish("完成")

    except FinishedException:
        raise FinishedException()
    except KeyError:
        await bag.finish("错误：背包为空")
    except IndexError:
        await bag.finish("错误：找不到物品")
    except Exception:
        await bot.send_group_msg(
            message=traceback.format_exc(),
            group_id=ctrlGroup
        )
        await bag.finish("处理失败")

# [HELPSTART]
# !Usage 1 bag
# !Info 1 查看自己的背包
# !Usage 2 bag view <背包物品id>
# !Info 2 查看背包中的物品
# !Usage 3 bag drop <背包物品id>
# !Info 3 丢弃背包中的物品
# [HELPEND]
