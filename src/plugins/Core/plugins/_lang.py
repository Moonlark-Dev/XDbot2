import json
import os
from nonebot.log import logger
import random


def reload():
    global _lang_user
    global _lang_dict
    if os.path.exists("data/lang.users.json"):
        with open("data/lang.users.json", encoding="utf-8") as f:
            _lang_user = json.load(f)
    else:
        with open("data/lang.users.json", "w", encoding="utf-8") as f:
            _lang_user = {}
            json.dump(_lang_user, f)

    _lang_files = os.listdir("src/plugins/Core/lang")
    _lang_dict = {}
    for _lang_file in _lang_files:
        try:
            _lang_index = json.load(
                open("src/plugins/Core/lang" + os.sep + _lang_file, encoding="utf-8")
            )
            _lang_dict[_lang_file.replace(".json", "")] = _lang_index
        except BaseException as e:
            logger.warning(f"加载 {_lang_file} 时发生错误：{e}")


def text(key: str, _format: list = [], _user: str | int = "default", params: dict = {}):
    user = str(_user)
    try:
        lang = _lang_user[user]
    except KeyError:
        lang = "zh_hans"
    if lang == "debug":
        return f"<{key}>"
    value = None
    try:
        value = _lang_dict[lang][key]
    except BaseException:
        try:
            value = _lang_dict["zh_hans"][key]
        except BaseException:
            # 在其他语言文件查找
            for l in list(_lang_dict.values()):
                if key in l.keys():
                    value = l[key]
                    break
            value = value if value else f"<本地化键缺失 {key}>"
    if isinstance(value, list):
        value = random.choice(value)
    for i in _format:
        value = value.replace("{}", str(i), 1)
    if params:
        for i in list(params.keys()):
            value = value.replace("${" + i + "}", params[i])
    if not (key.endswith("_nb") or key.endswith("__base__")) \
            and (len(split_key := key.split(".")) >= 2) \
            and not (based_value := text(split_key[0] + ".__base__", [value], user)).startswith("<本地化键缺失"):
        return based_value
    return str(value)


def _load_key(langname, key, default=None):
    try:
        value = _lang_dict[langname][key]
        if isinstance(value, list):
            value = random.choice(value)
        return value
    except BaseException:
        return default if default else key


reload()
