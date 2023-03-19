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
            with open("data/lang.users.json", "r") as f:
                _lang_user = json.load(f)
            _lang_user[event.get_user_id()] = args
            with open("data/lang.users.json", "w") as f:
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
                key_length = 0
                for key in _lang._lang_dict["zh_hans"].keys():
                    if key not in ["lang.version", "lang.author"]:
                        if key in _lang._lang_dict[lang_name].keys():
                            found_key += 1
                        key_length += 1

                try: version = _lang._lang_dict[lang_name]["lang.version"]
                except: version = "v1.0.0"
                try: author = _lang._lang_dict[lang_name]["lang.author"]
                except: author = "未知创作者"

                await lang.finish("\n".join((
                    "「语言详细信息」",
                    f"名称：{lang_name}",
                    f"版本：{version}",
                    f"作者：{author}",
                    f"兼容性：{found_key} / {key_length} {found_key / key_length * 100}%"
                )))

        else:
            await lang.finish(_lang.text("lang.notfound", [args], event.get_user_id()))
