import json
from random import randint, random

items = json.load(open("data/etm.items.json", encoding="utf-8"))
defaultItemData = {
    "displayName": None,
    "information": None,
    "canUse": True,
    "canSell": True,
    "canDrop": True
}


class ItemCanNotRemove(Exception):
    pass


class NotHaveEnoughItem(Exception):
    pass


def addItem(userID: str, itemID: str, count: int, itemData: dict):
    users = json.load(open("data/etm.bag.json", encoding="utf-8"))
    if userID not in list(users.keys()):
        users[userID] = []
    data = defaultItemData.copy()
    data.update(items[itemID]["data"])
    data.update(itemData)
    length = 0
    for item in users[userID]:
        if item["id"] == itemID and item["data"] == data:
            users[userID][length]["count"] += count
            break
        length += 1
    if length == users[userID].__len__():
        users[userID] += [
            {
                "id": itemID,
                "count": count,
                "data": data
            }
        ]
    json.dump(users, open("data/etm.bag.json", "w", encoding="utf-8"))


def removeItemsFromBag(userID: str, itemPos: int, count: int,
                       removeType: str = "Use", ignoreData: bool = False):
    userData = json.load(open("data/etm.bag.json", encoding="utf-8"))
    if userID not in list(userData.keys()):
        userData[userID] = []
    if userData[userID][itemPos]["data"][f"can{removeType}"] or ignoreData:
        if userData[userID][itemPos]["count"] > count:
            userData[userID][itemPos]["count"] -= count
        elif userData[userID][itemPos]["count"] == count:
            userData[userID].pop(itemPos)
        else:
            raise NotHaveEnoughItem()
    else:
        raise ItemCanNotRemove()
    json.dump(userData, open("data/etm.bag.json", "w", encoding="utf-8"))


def removeItemsByID(userID: str, itemID: str, itemCount: int,
                    removeType: str = "Use"):
    userData = json.load(open("data/etm.bag.json", encoding="utf-8"))
    if userID not in userData.keys():
        userData[userID] = []
    count = itemCount
    length = 0
    bag = userData[userID].copy()
    for item in bag:
        if item["id"] == itemID and item["data"][f"can{removeType}"]:
            if item["count"] > count:
                userData[userID][length]["count"] -= count
                json.dump(
                    userData,
                    open(
                        "data/etm.bag.json",
                        "w",
                        encoding="utf-8"))
                return True
            elif item["count"] == count:
                userData[userID].pop(length)
                json.dump(
                    userData,
                    open(
                        "data/etm.bag.json",
                        "w",
                        encoding="utf-8"))
                return True
            else:
                count -= userData[userID].pop(length)["count"]
                length -= 1
        length += 1
    # 丢弃更改
    return False

def removeItemsByID_allowBelowZero(userID: str, itemID: str, itemCount: int, removeType: str = "Use", itemData: dict = {}):
    userData = json.load(open("data/etm.bag.json", encoding="utf-8"))
    if userID not in userData.keys():
        userData[userID] = []
    count = itemCount
    length = 0
    bag = userData[userID].copy()
    for item in bag:
        if item["id"] == itemID and item["data"][f"can{removeType}"]:
            if item["count"] != count:
                userData[userID][length]["count"] -= count
                json.dump(
                    userData,
                    open(
                        "data/etm.bag.json",
                        "w",
                        encoding="utf-8"))
                return True
            elif item["count"] == count:
                userData[userID].pop(length)
                json.dump(
                    userData,
                    open(
                        "data/etm.bag.json",
                        "w",
                        encoding="utf-8"))
                return True
        length += 1
    addItem(userID,itemID,0-itemCount,itemData)
    return True

def useItem(userID: str, pos: int):
    userData = json.load(open("data/etm.bag.json", encoding="utf-8"))
    item = userData[userID][pos]
    vipLevel = json.load(
        open(
            "data/etm.userData.json",
            encoding="utf-8"))[userID]["vip"]["level"]
    removeItemsFromBag(userID, pos, 1)
    # 处理物品
    if item["id"] == "2":
        # 每日VimCoin礼包
        if random() <= 0.05:
            count = randint(30, 50)
        elif random() <= 0.1:
            count = randint(0, 30)
        elif random() <= 0.2:
            count = randint(0, 25)
        else:
            count = randint(0, 15)
        # VIP加成
        if vipLevel:
            count *= 1 + (vipLevel / 75 * 2)
        addItem(userID, "0", int(count), dict())
        return f"你获得了：\n1. VimCoin x{int(count)}"
    elif item["id"] == "3":
        # 20面骰子
        num = randint(1, 20)
        if num == 20:
            addItem(userID, "0", 50, {})
            return "买了一颗二十面骰，掷出了 20，大成功，获得了 50vi！"
        elif 18 <= num <= 19:
            addItem(userID, "0", 20, {})
            return f"买了一颗二十面骰，掷出了 {num}，运气绝佳，获得了 20vi！"
        elif 15 <= num <= 17:
            addItem(userID, "0", 10, {})
            return f"买了一颗二十面骰，掷出了 {num}，运气不错，获得了 10vi！"
        elif 10 <= num <= 14:
            addItem(userID, "0", 5, {})
            return f"买了一颗二十面骰，掷出了 {num}，拿回了自己的 5vi！"
        elif 2 <= num <= 9:
            return f"买了一颗二十面骰，掷出了 {num}，一无所获……"
        elif num == 1:
            removeItemsByID_allowBelowZero(userID, "0", 50, itemData={})
            return f"买了一颗二十面骰，掷出了 {num}，大失败，倾家荡产，丢失了 50vi！"

    else:
        addItem(userID, item["id"], 1, item["data"])
        return "你在尝试着什么……"


def addExp(userID: str, exp: int):
    data = json.load(open("data/etm.userData.json", encoding="utf-8"))
    try:
        data[userID]["exp"] += exp
    except KeyError:
        data[userID] = {
            "level": 1,
            "exp": exp,
            "title": None,
            "vip": {
                "level": None,
                "endTime": None
            }
        }
    while True:
        if data[userID]["exp"] >= data[userID]["level"] ** 2:
            data[userID]["exp"] -= data[userID]["level"] ** 2
            data[userID]["level"] += 1
        else:
            break
    json.dump(data, open("data/etm.userData.json", "w", encoding="utf-8"))


def getCountOfItem(userID: str, itemID: str):
    data = json.load(open("data/etm.bag.json", encoding="utf-8"))
    count = 0
    try:
        for item in data[userID]:
            if item["id"] == itemID:
                count += item["count"]
    except KeyError:
        pass
    return count


"""
def useItems(userID: str, pos: int, count: int):
    output = []
    for _ in range(count):
        try:
            r = useItem(userID, pos)
        except:
            return output
        else:
            output += r
    return output
"""
