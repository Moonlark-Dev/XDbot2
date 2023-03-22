from nonebot import on_command
from nonebot.adapters.onebot.v11 import Message, MessageEvent
from nonebot.params import CommandArg
from . import _lang, _error
import json
import traceback
import os

lang = on_command("lang", aliases={"语言"})


@lang.handle()
async def lang_handle(event: MessageEvent, message: Message = CommandArg()):
    try:
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
                    _lang.text("lang.list", [
                               "\n".join(ls)], event.get_user_id())
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

                    author = _lang._load_key(lang_name, "lang.author", "未知创作者")
                    version = _lang._load_key(
                        lang_name, "lang.version", "v1.0.0")

                    await lang.send("\n".join((
                        _lang.text('lang.intro', [], event.get_user_id()),
                        _lang.text('lang.lang_name', [
                                   lang_name], event.get_user_id()),
                        _lang.text('lang.lang_version', [
                                   version], event.get_user_id()),
                        _lang.text('lang.lang_author', [
                                   author], event.get_user_id()),
                        _lang.text('lang.compatibility',
                                   [found_key, key_length, round(
                                       found_key / key_length * 100)],
                                   event.get_user_id())

                        #                     不是很能理解，很没必要，先注释了——XiaoDeng3386
                        #                     f"{_lang.text(lang_name, 'lang.text.intro')}",
                        #                     f"{_lang._load_key(lang_name, 'lang.text.name')}{lang_name}",
                        #                     f"{_lang._load_key(lang_name, 'lang.text.version')}{version}",
                        #                     f"{_lang._load_key(lang_name, 'lang.text.author')}{author}",
                        #                     f"{_lang._load_key(lang_name, 'lang.text.compatibility')}{found_key} / {key_length} {round(found_key / key_length * 100)}%"
                    )))

                    if missing_keys:
                        await lang.finish(_lang.text('lang.keylost', [" ".join(missing_keys)], event.get_user_id()))
                    else:
                        await lang.finish()

            else:
                await lang.finish(_lang.text("lang.notfound", [args], event.get_user_id()))
    except BaseException:
        await _error.report(traceback.format_exc(), lang)
