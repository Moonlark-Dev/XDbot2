import json
import os


def reload():
    global _lang_user
    global _lang_dict
    if os.path.exists("data/lang.users.json"):
        with open("data/lang.users.json", "r") as f:
            _lang_user = json.load(f)
    else:
        with open("data/lang.users.json", "w") as f:
            _lang_user = {}
            json.dump(_lang_user, f)

    _lang_files = os.listdir("src/plugins/Core/lang")
    _lang_dict = {}
    for _lang_file in _lang_files:
        _lang_index = json.load(open("src/plugins/Core/lang" + os.sep + _lang_file))
        _lang_dict[_lang_file.replace(".json", "")] = _lang_index


def text(key: str, _format: list = [], user: str = "default", params: dict = {}):
    try:
        lang = _lang_user[user]
    except KeyError:
        lang = "zh_fzz"
    if lang == "debug":
        return f"<{key}>"
    try:
        value = _lang_dict[lang][key]
    except BaseException:
        try:
            value = _lang_dict["zh_fzz"][key]
        except BaseException:
            return f"<本地化键缺失 {lang}.json {key}>"
    for i in _format:
        value = value.replace("{}", str(i), 1)
    if params:
        for i in list(params.keys()):
            value = value.replace("${" + i + "}", params[i])
    return str(value)


reload()
