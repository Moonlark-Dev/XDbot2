import json
import os
import os.path

# 快捷访问
from nonebot import on_shell_command
from nonebot import on_command
from nonebot.rule import ArgumentParser
from nonebot.permission import SUPERUSER
from nonebot.params import CommandArg
from nonebot.matcher import Matcher
from . import _error as error
from . import _lang as lang
from nonebot.adapters.onebot.v11 import GroupMessageEvent
from nonebot.adapters.onebot.v11 import MessageEvent
from nonebot.adapters.onebot.v11 import Message

# import traceback

class Json:

    def __init__(self, path: str) -> None:
        self.path = os.path.join("data", path)
        
        try:
            os.makedirs(os.path.dirname(self.path))
        except:
            pass

        if not os.path.isfile(self.path):
            self.data = {}
        else:
            self.data = json.load(open(self.path, encoding="utf-8"))

    def __setitem__(self, key: str, value: any) -> None:
        if value == None:
            self.data.pop(str(key))
        self.data[str(key)] = value

    def pop(self, key: str) -> any:
        try:
            return self.data.pop(key)
        except:
            return None

    # def __getattr__(self, item: str) -> any:
        # return self.get(item)

    def __getitem__(self, key: str) -> any:
        return self.get(key)

    def __del__(self) -> None:
        json.dump(self.data, open(self.path, "w", encoding="utf-8"))

    def get(self, key: str, default: any = None) -> None:
        try:
            return self.data[key]
        except:
            if default == None:
                return None
            self.data[key] = default
            return self.get(key, default)

    def items(self):
        return list(self.data.items())
