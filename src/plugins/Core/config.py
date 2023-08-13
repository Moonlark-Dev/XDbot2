from pydantic import BaseSettings
import json
import time


class Config(BaseSettings):
    # Your Config Here
    # 版本常量
    VERSION = "v2.8.271"
    # 控制中心
    CONTROL_GROUP = "598443695"

    # 初始化
    DIRECTORIES = ["data", "data/caveImages", "data/rules", "data/etm"]
    # 数据文件命名规则：子插件.数据名.json
    FILES = [
        {"path": "data/cave.latest_use.json", "text": "{}"},
        {"path": "data/su.update_notice.json", "text": '{"disabled": []}'},
        {"path": "data/mcver.mc_cache_version.txt", "text": ""},
        {"path": "data/mcver.mc_update_notice.enabled.json", "text": "[]"},
        {"path": "data/su.mails.json", "text": "{}"},
        {"path": "data/cave.banned.json", "text": "[]"},
        {
            "path": "data/bank.config.json",
            "text": json.dumps({"interest_rate": 0.015, "max_lead": 100}),
        },
        {"path": "data/market.average.json", "text": "{}"},
        {
            "path": "data/gpt.config.json",
            "text": json.dumps(
                {"api_key": "", "workspace": "gpt-4", "plugin": "gpt-4", "sleep": 1}
            ),
        },
        {"path": "data/_error.count.json", "text": json.dumps({"count": 0})},
        {
            "path": "data/chatgpt.config.json",
            "text": json.dumps({"proxy": "http://127.0.0.1:7890", "api_key": ""}),
        },
        {"path": "data/chatgpt.messages.json", "text": json.dumps({})},
        {"path": "data/market.items.json", "text": "{}"},
        {"path": "data/email.reminded.json", "text": "{}"},
        {"path": "data/github.config.json", "text": "{}"},
        {
            "path": "data/etm/vim.json",
            "text": json.dumps(
                {
                    "in": 0,
                    "out": 0,
                    "exchange_rate": 1,
                    "_exchange_rate": 0.58,
                    "item_count": 500,
                }
            ),
        },
        {"path": "data/quick_math.average.json", "text": json.dumps({"average": 0})},
        {"path": "data/quick_calculus.enabled_groups.json", "text": "[]"},
        {"path": "data/quick_math.enabled_groups.json", "text": "[]"},
        {"path": "data/ghot.stamps.json", "text": "{}"},
        {"path": "data/ghot.day.json", "text": "{}"},
        {"path": "data/ghot.total.json", "text": "{}"},
        {"path": "data/etm/achievement_progress.json", "text": "{}"},
        {
            "path": "data/etm/vimcoin.json",
            "text": json.dumps({"in": 0, "out": 0, "exchange_rate": 1}),
        },
        {"path": "data/etm/achievement.json", "text": "{}"},
        {"path": "data/etm/sign.json", "text": json.dumps({"latest": {}, "days": {}})},
        {"path": "data/etm/users.json", "text": "{}"},
        {"path": "data/etm/bags.json", "text": "{}"},
        {
            "path": "data/random_events.disable.json",
            "text": json.dumps(
                {"send_images": [], "download_images": [], "random_give": []}
            ),
        },
        {"path": "data/setu.allow.json", "text": json.dumps({"r18": False})},
        {"path": "data/jrrp.users.json", "text": "{}"},
        {"path": "data/smart_reply.data.json", "text": '{"count":0}'},
        {"path": "data/cave.comments.json", "text": "{}"},
        {"path": "data/rule.rules.json", "text": "[]"},
        {"path": "data/messenger.messageList.json", "text": "[]"},
        {"path": "data/ctrl.json", "text": json.dumps({"control": CONTROL_GROUP})},
        {"path": "data/ct.globalData.json", "text": "{}"},
        {"path": "data/su.blackList.json", "text": "[]"},
        {"path": "data/init.disabled.json", "text": "[]"},
        {
            "path": "data/cave.data.json",
            "text": json.dumps({"count": 0, "data": dict()}),
        },
        {"path": "data/su.priority_accout.json", "text": '{"accouts":[]}'},
        {"path": "data/forward.groupList.json", "text": "[]"},
        {"path": "data/ban.banData.json", "text": "{}"},
        {"path": "data/vote.list.json", "text": "{}"},
        {
            "path": "data/reply.images.json",
            "text": json.dumps({"A": [], "B": [], "C": [], "review": dict()}),
        },
        {"path": "data/whoAtme.data.json", "text": "{}"},
        {"path": "data/sixcount.data.json", "text": "{}"},
        {
            "path": "data/sixcount.starttime.json",
            "text": json.dumps({"time": time.time()}),
        },
        {
            "path": "data/setu.config.json",
            "text": json.dumps(
                {"sleep": 45, "delete_sleep": 25, "proxies": "http://127.0.0.1:7890"}
            ),
        },
        {"path": "data/setu.count.json", "text": "{}"},
        {"path": "data/cave.data.restore.json", "text": "{}"}
        # ,
        # {
        #    "path": "data/rule.rules.json",
        #    "text": "[]"
        # }
    ]

    class Config:
        extra = "ignore"


"""{
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
                    "name": "VimCoin礼包",
                    "info": "来自XDbot某个贡献者的一点小心意\n打开后可获得：\n1. VimCoin x0~50",
                    "data": {}
                },
                "3": {
                    "name": "二十面骰",
                    "info": "二十面骰子，致敬LTW3",
                    "data": {}
                },
                "4": {
                    "name": "书与笔",
                    "info": "致敬 Minecraft，用于书写文本",
                    "data": {"author": None, "text": None, "saved": False, "displayName": "书与笔"}
                },
                "5": {
                    "name": "命名牌",
                    "info": "用于修改物品显示及简介",
                    "data": {}
                }
            })
        },"""
