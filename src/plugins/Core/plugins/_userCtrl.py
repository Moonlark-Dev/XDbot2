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
    if userID not in list(userData.keys()):
        userData[userID] = []
    count = itemCount
    length = 0
    for item in userData[userID]:
        if item["id"] == itemID and item["data"][f"can{removeType}"]:
            if item["count"] > count:
                userData[userID][length]["count"] -= count
                json.dump(userData, open("data/etm.bag.json", "w", encoding="utf-8"))
                return True
            elif item["count"] == count:
                userData[userID].pop(length)
                json.dump(userData, open("data/etm.bag.json", "w", encoding="utf-8"))
                return True
            else:
                count -= userData[userID].pop(length)["count"]
    if count == 0:
        # 保存操作
        json.dump(userData, open("data/etm.bag.json", encoding="utf-8"))
        return True
    else:
        # 丢弃更改
        return False


def useItem(userID: str, pos: int):
    userData = json.load(open("data/etm.bag.json", encoding="utf-8"))
    item = userData[userID][pos]
    vipLevel = json.load(open("data/etm.userData.json", encoding="utf-8"))[userID]["vip"]["level"]
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
                "buyTime": None
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
