# TODO 重写兼容 XDbot2 环境

import os
import re
from typing import cast, Dict, Any, Match, Union, TypeAlias, Literal

import yaml

from nonebot.adapters.onebot.v11 import MessageEvent

from ._store import JsonDict
from ._onebot import UserID


Tree: TypeAlias = Dict[str, Union["Tree", str]]
LangTag = Literal["en", "zh-hans"]  # TODO: 与`./lang/`文件夹下语言文件同步

langs: Dict[LangTag, Tree] = {}
lang_use = JsonDict("lang_use.json", lambda: "zh-hans")


for filename in os.listdir("lang"):
    lang = cast(LangTag, os.path.splitext(filename)[0])
    file_path = os.path.join("lang", filename)
    with open(file_path, "r", encoding="utf-8") as file:
        langs[lang] = yaml.safe_load(file)


def text(__lang: LangTag | UserID | MessageEvent, __key: str, **kwargs: Any) -> str:
    lang, key = __lang, __key
    if isinstance(lang, MessageEvent):
        lang = lang.user_id
    lang = str(lang)
    if lang.isdecimal():
        lang = lang_use[lang]
    lang = cast(LangTag, lang)

    def gets(data: Tree, key: str) -> str:
        for subkey in key.split("."):
            data = cast(Tree, data[subkey])
        return cast(str, data)

    try:
        data = gets(langs[lang], key)
    except KeyError:
        lang = lang_use.default_factory()
        data = gets(langs[cast(LangTag, lang)], key)

    def repl(match: Match[str]) -> str:
        matched = match.group()
        expr = matched[2:-2]
        try:
            return str(eval(expr.strip(), {"__builtins__": None}, kwargs))
        except Exception:
            return matched

    return re.sub("{{.*?}}", repl, data, flags=re.DOTALL)
