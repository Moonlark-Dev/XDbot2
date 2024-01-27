# from plugins.Core.plugins.etm.item import Item
from .. import json2items
from ..item_basic_data import BASIC_DATA
from nonebot_plugin_apscheduler import scheduler
from nonebot import require
from .. import economy
from .. import data
from .. import exp
from .overflow import add_overflow
from ..items import rubbish

require("nonebot_plugin_apscheduler")

# items.json2items(json.load(open("data/etm/bags.json", encoding="utf-8")))
bags = {}


def get_bags():
    for user, bag in list(data.bags.items()):
        bags[user] = json2items.json2items(bag, user)


get_bags()


def get_items_count_in_bag(user_id):
    user_id = str(user_id)
    count = 0
    bag = bags[user_id]
    for item in bag:
        count += item.count
    return count


@scheduler.scheduled_job("cron", second="*/3", id="save_bags")
def save_bags():
    bag_data = {}
    for user_id, bag in list(bags.items()):
        bag_data[user_id] = []
        for item in bag:
            if item.count > 0:
                # 处理nbt
                nbt = item.data.copy()
                for key in list(BASIC_DATA.keys()):
                    try:
                        if nbt[key] == BASIC_DATA[key]:
                            nbt.pop(key)
                    except BaseException:
                        pass
                for key in list(item.basic_data.keys()):
                    try:
                        if nbt[key] == item.basic_data[key]:
                            nbt.pop(key)
                    except BaseException:
                        pass
                bag_data[user_id].append(
                    {"id": item.item_id, "count": item.count, "data": nbt.copy()}
                )
    data.bags = bag_data
    get_bags()
    # 超出容量处理
    # for user in list(bags.keys()):
    #     count = get_items_count_in_bag(user)
    #     if count > 128:
    #         economy._add_vimcoin(user, -0.001 * (count - 128))


def get_user_bag(user_id):
    try:
        return bags[str(user_id)]
    except KeyError:
        bags[user_id] = []
        return bags[str(user_id)]


def _add_item(user_id, item):
    try:
        if len(bags[str(user_id)]) >= 32:
            add_overflow(user_id, item.item_id, item.count, item.data)
            return
        bags[str(user_id)].append(item)
    except KeyError:
        bags[str(user_id)] = [item]


def add_item(user_id, item_id, item_count=1, item_data={}):
    user_id = str(user_id)
    if item_id == "vimcoin":
        economy.add_vi(user_id, item_count)
        return
    elif item_id == "exp":
        exp.add_exp(user_id, item_count)
        return
    try:
        for item in bags[user_id]:
            if item.item_id == item_id:
                item_count -= item.add(item_count, item_data)
        if item_count > 0:
            _add_item(
                user_id, json2items.ITEMS[item_id](item_count, item_data, user_id)
            )
    except KeyError:
        bags[user_id] = []
        add_item(user_id, item_id, item_count, item_data)


async def use_item(user_id, item_pos, argv=""):
    user_id = str(user_id)
    return await bags[user_id][item_pos].on_use(argv)


rubbish.add_item = add_item
