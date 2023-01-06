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
        "data"
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
        }
    ]

    class Config:
        extra = "ignore"
