import json,os

if os.path.exists("data/lang.users.json"):
    with open("data/lang.users.json","r") as f:
        _lang_user = json.load(f)
else:
    with open("data/lang.users.json","w") as f:
        _lang_user = {}
        json.dump(_lang_user,f)

_lang_files = os.listdir("src/plugins/Core/lang")
_lang_dict = {}
for _lang_file in _lang_files:
    _lang_index = json.load(open("src/plugins/Core/lang" + os.sep + _lang_file))
    _lang_dict[_lang_file.replace(".json","")] = _lang_index


async def text(key: str, _format: list = [], user: str = "default"):
    try:
        lang = _lang_user[user]
    except KeyError:
        lang = "zh_fzz"
    try:
        value = _lang_dict[lang][key]
    except:
        value = f"<本地化键缺失 {lang}.json → {key}>"
    for i in _format:
        value = value.replace("{}",str(i),1)
    return str(value)
