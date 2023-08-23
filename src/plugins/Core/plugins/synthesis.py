from ._utils import *
from .etm import bag, exp, items
from .etm.item import Item
import os
import math

def get_item_list() -> list:
    file_list = os.listdir("src/plugins/Core/synthesis/")
    item_list = []
    for file in file_list:
        if (not file.startswith("_")) and file.endswith(".json"):
            item_list.append(Json(os.path.join("../src/plugins/Core/synthesis/", file)).to_dict())
    return sorted(item_list, key=lambda x: x["id"])

def items2text(item_list: list[Item]) -> str:
    text = ""
    length = 0
    for item in item_list:
        length += 1
        text += f"\n {length}. {item.data['display_name']} x{item.count}"
    return text[1:]
    
def list_items(page: int, self_id: int, user_id: int) -> list[dict]:
    item_list = get_item_list()
    node_messages = [{
        "type": "node",
        "data": {
            "uin": self_id,
            "nickname": "XDbot2",
            "content": lang.text("synthesis.list_title", [page, math.ceil(len(item_list) / 100)], user_id)
        }
    }]

    for item_data in item_list[100*(page-1):100*page]:
        result_items = items.json2items(item_data["result"])
        required_items = items.json2items(item_data["required"])
        node_messages.append({
            "type": "node",
            "data": {
                "uin": self_id,
                "nickname": "XDbot2",
                "content": lang.text("synthesis.list_item", [
                    str(item_data["id"]),
                    items2text(result_items),
                    items2text(required_items)
                ], user_id)
            }
        })
    return node_messages
  
def get_page(argv: list):
    try:
        return int(argv[1])
    except:
        return 1

@on_command("synthesis", aliases={"合成"}).handle()
async def handle_synthesis_command(bot: Bot, event: MessageEvent, message: Message = CommandArg()):
    try:
        argv = message.extract_plain_text().split(" ")
        match argv[0]:
            case "" | "list":
                await bot.call_api(
                    f"send_{'group' if event.get_session_id().split('_')[0]  == 'group' else 'private'}_forward_msg",
                    messages=list_items(get_page(argv), event.self_id, event.user_id),
                    user_id=int(event.get_user_id()),
                    group_id=event.dict().get("group_id"),
                )

    except:
        await error.report()