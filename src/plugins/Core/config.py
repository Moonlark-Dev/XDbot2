from pydantic import BaseSettings
import json


class Config(BaseSettings):
    # Your Config Here
    DIRECTORIES = [
        "data"
    ]
    # 数据文件命名规则：子插件.数据名.json
    FILES = [
        {
            "path": "data/jrrp.users.json",
            "text": "{}"
        }
    ]
    # 版本常量
    VERSION = "1.0.0"

    class Config:
        extra = "ignore"
