from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, Message, MessageEvent
from nonebot.params import CommandArg
from . import _lang
import json
import os

lang = on_command("lang", aliases={"语言"})


@lang.handle()
async def lang_handle(bot: Bot, event: MessageEvent, message: Message = CommandArg()):
    args = message.extract_plain_text()
    if args == "":
        await lang.finish(
            _lang.text("lang.empty", ["/lang <lang>"], event.get_user_id())
        )
    else:
        if os.path.exists(
                f"src/plugins/Core/lang/{args}.json") or args == "debug":
            with open("data/lang.users.json", encoding="utf-8") as f:
                _lang_user = json.load(f)
            _lang_user[event.get_user_id()] = args
            with open("data/lang.users.json", "w", encoding="utf-8") as f:
                json.dump(_lang_user, f)
            _lang.reload()
            await lang.finish(_lang.text("lang.success", [args], event.get_user_id()))
        elif args == "list":
            ls = os.listdir("src/plugins/Core/lang")
            for i in range(len(ls)):
                ls[i] = ls[i].replace(".json", "")
            await lang.finish(
                _lang.text("lang.list", ["\n".join(ls)], event.get_user_id())
            )
        elif args.split(" ")[0] == "view":
            lang_name = args.split(" ")[1]
            if lang_name in _lang._lang_dict.keys():
                found_key = 0
                missing_keys = []
                key_length = 0
                for key in _lang._lang_dict["zh_hans"].keys():
                    if key not in ["lang.version", "lang.author"]:
                        if key in _lang._lang_dict[lang_name].keys():
                            found_key += 1
                        else:
                            missing_keys.append(key)
                        key_length += 1

                version = _lang._load_key(lang_name, "lang.version")
                author = _lang._load_key(lang_name, "lang.author")

                await lang.send("\n".join((
                    f"{_lang._load_key(lang_name, 'lang.text.intro')}",
                    f"{_lang._load_key(lang_name, 'lang.text.name')}{lang_name}",
                    f"{_lang._load_key(lang_name, 'lang.text.version')}{version}",
                    f"{_lang._load_key(lang_name, 'lang.text.author')}{author}",
                    f"{_lang._load_key(lang_name, 'lang.text.compatibility')}{found_key} / {key_length} {round(found_key / key_length * 100)}%"
                )))
                if missing_keys:
                    await lang.finish(f"{_lang._load_key(lang_name, 'lang.text.keylost')}" + " ".join(missing_keys))
                else:
                    await lang.finish()

        else:
            await lang.finish(_lang.text("lang.notfound", [args], event.get_user_id()))
