from pydantic import BaseSettings
import json


class Config(BaseSettings):
    # Your Config Here
    # 版本常量
    VERSION = "1.0.0"
    # 控制中心
    CONTROL_GROUP = "598443695"

    # 初始化
    DIRECTORIES = [
        "data",
        "data/caveImages"
    ]
    # 数据文件命名规则：子插件.数据名.json
    FILES = [
        {
            "path": "data/jrrp.users.json",
            "text": "{}"
        },
        {
            "path": "data/messenger.messageList.json",
            "text": "[]"
        },
        {
            "path": "data/ctrl.json",
            "text": json.dumps({"control": CONTROL_GROUP})
        },
        {
            "path": "data/ct.globalData.json",
            "text": "{}"
        },
        {
            "path": "data/su.blackList.json",
            "text": '[]'
        },
        {
            "path": "data/init.disabled.json",
            "text": "[]"
        },
        {
            "path": "data/cave.data.json",
            "text": json.dumps({
                "count": 0,
                "data": dict()
            })
        },
        {
            "path": "data/etm.bag.json",
            "text": "{}"
        },
        {
            "path": "data/etm.items.json",
            "text": json.dumps({
                "0": {
                    "name": "VimCoin",
                    "info": "XDbot2 通用货币",
                    "data": {
                        "canDrop": False,
                        "canSell": False
                    }
                },
                "1": {
                    "name": "FZSGBall",
                    "info": "球你tm不女装我还不删了！（",
                    "data": {}
                },
                "2": {
                    "name": "每日VimCoin礼包",
                    "info": "打开后可获得：\n1. VimCoin x0~50",
                    "data": {}
                }
            })
        },
        {
            "path": "data/sign.latestTime.json",
            "text": "{}"
        },
        {
            "path": "data/sign.signDay.json",
            "text": "{}"
        },
        {
            "path": "data/etm.userData.json",
            "text": "{}"
        },
        {
            "path": "data/forward.groupList.json",
            "text": "[]"
        },
        {
            "path": "data/shop.items.json",
            "text": json.dumps({
                "0": {
                    "name": "VimCoin",
                    "count": 2,
                    "price": 114,
                    "seller": {
                        "nickname": "StarWorld",
                        "user_id": "2915495930"
                    },
                    "info": "XDbot2 通用货币",
                    "item": {
                        "id": "0",
                        "count": None,
                        "data": {}
                    }
                }
            })
        },
        {
            "path": "data/autosell.items.json",
            "text": json.dumps([
                {
                    "id": "0",
                    "count": 5,
                    "price": 5,
                    "data": {}
                }
            ])
        },
        {
            "path": "data/autosell.latest.json",
            "text": "{\"mday\":0}"
        }
    ]

    class Config:
        extra = "ignore"
