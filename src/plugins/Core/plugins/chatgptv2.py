from .etm import economy
from .su import su
from ._utils import *
import openai

openai.proxy = Json("chatgpt.config.json")["proxy"]
openai.api_key = Json("chatgpt.config.json")["api_key"]

# [HELPSTART] Version: 2
# Command: gpt
# Info: XDbot2GPT
# Usage: gpt info
# Usage: gpt reset [模板]
# Usage: gpt switch {global|group|private}
# Usage: gpt token buy <数量>
# Usage: gpt <内容>
# [HELPEND]
# TODO 未完成内容：
# Usage: gpt show [会话ID]
# Usage: gpt load <会话永久ID>
# Usage: gpt upload [会话ID]
# Usage: gpt retry
# Usage: gpt back



def get_user_info(user_id: str) -> str:
    user_data = Json(f"gpt/users/{user_id}.json")
    return lang.text("chatgpt.user_info", [
        user_data["token"] or 0,
        user_data["free"] or 0
    ], user_id)


def init_session(session_id: str, system_message: str | None, force_unlock: bool = False) -> bool:
    if force_unlock:
        Json(f"gpt/sessions/{session_id}.json")["is_locked"] = False
    if Json(f"gpt/sessions/{session_id}.json")["is_locked"]:
        return FAILED
    if not system_message:
        Json(f"gpt/sessions/{session_id}.json")["messages"] = []
    else:
        Json(f"gpt/sessions/{session_id}.json")["messages"] = [{
            "role": "system",
            "content": system_message
        }]
    return SUCCESS


def get_template_by_name(template_name: str) -> str | None:
    try:
        with open(f"src/plugins/Core/chatgpt_template/{template_name}.txt", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return None


def reset_session(session_id: str, template: str | None = None, force_unlock: bool = False, _system_message: str | None = None) -> bool:
    system_message = get_template_by_name(template) or _system_message # type: ignore
    return init_session(session_id, system_message, force_unlock)


def get_user_session(user_id: str) -> str:
    return Json(f"gpt/users/{user_id}.json")["session"] or f"u{user_id}"

def get_session_by_id(session_id: str) -> Json:
    return Json(f"gpt/sessions/{session_id}.json")

def change_session(user_id: str, session: str) -> None:
    Json(f"gpt/users/{user_id}.json")["session"] = session


def check_user_tokens(user_id: str) -> bool:
    user_data = Json(f"gpt/users/{user_id}.json")
    return user_data.get("token", 0) > 0 or user_data.get("free", 0) > 0


def get_session_messages(session_id: str) -> list[dict]:
    if Json(f"gpt/sessions/{session_id}.json")["messages"]:
        return Json(f"gpt/sessions/{session_id}.json")["messages"]
    else:
        reset_session(session_id, "default", True)
        return get_session_messages(session_id)


async def get_chatgpt_reply(messages: list[dict], model: str = "gpt-3.5-turbo"):
    return await openai.ChatCompletion.acreate(messages=messages, model=model)


def add_message_to_session(session_id: str, role: str, content: str) -> None:
    messages = get_session_by_id(session_id).get("messages", [])
    get_session_by_id(session_id)["messages"] = messages + [{
        "role": role,
        "content": content
    }]


def reduce_tokens(user_id: str, token_count: int) -> int:
    user_data = Json(f"gpt/users/{user_id}.json")
    if user_data.get("free", 0) > 0:
        user_data["free"] -= 1
        return 0
    else:
        user_data["token"] -= token_count
        return token_count


def generate_gpt_reply(gpt_reply: str, used_token: int, user_id: str) -> str:
    if used_token > 0:
        token_usage_msg = lang.text(
            "chatgpt.used_token", 
            [
                Json(f"gpt/users/{user_id}.json")["token"],
                used_token
            ],
            user_id
        )
    else:
        token_usage_msg = lang.text(
            "chatgpt.free",
            [
                Json(f"gpt/users/{user_id}.json")["free"]
            ],
            user_id
        )
    return lang.text(
        "chatgpt.reply", 
        [
            token_usage_msg,
            gpt_reply
        ],
        user_id
    )


@su.handle()
async def handle_su_gpt(message: Message = CommandArg()) -> None:
    try:
        arguments = message.extract_plain_text().split(" ")
        if arguments[0] == "gpt":
            if arguments[1] in ["tokens", "token", "t"]:
                if arguments[2] in ["add"]:
                    user_data = Json(f"gpt/users/{arguments[3]}.json")
                    user_data["token"] = user_data.get("token", 0) + int(arguments[4])
                    await su.finish("完成！")
    except:
        await error.report()
            

@on_command("gpt").handle()
async def handle_gpt_command(matcher: Matcher, event: GroupMessageEvent, message: Message = CommandArg()) -> None:
    try:
        argv = message.extract_plain_text().split(" ")
        user_id = event.get_user_id()

        match argv[0]:

            case "info":
                await matcher.finish(get_user_info(user_id))

            case "reset":
                is_reset_successful = reset_session(
                    get_user_session(user_id),
                    get_list_item(argv, 1, "default"),
                    _system_message=" ".join(argv[1:]))
                if is_reset_successful:
                    await matcher.finish(lang.text(
                        "chatgpt.reset_successful",
                        [get_user_session(user_id)],
                        user_id))
                else:
                    await matcher.finish(
                        lang.text("chatgpt.reset_error", [], user_id))

            case "switch":
                try:
                    change_session(user_id, {
                        "global": "global",
                        "group": f"g{event.group_id}",
                        "private": f"u{user_id}"
                    }[argv[1]])
                except KeyError:
                    await matcher.finish(lang.text("chatgpt.need_session_argv", [], user_id))
                except IndexError:
                    await matcher.finish(lang.text("chatgpt.session_not_available", [], user_id))
                await matcher.finish(lang.text("chatgpt.switched_to_another_session", [argv[1]], user_id))

            case "token" | "tokens":
                if argv[1] in ["buy", "购买"]:
                    count = max(int(argv[2]), 0)
                    if economy.use_vimcoin(user_id, 0.04 * count):
                        Json(f"gpt/users/{user_id}.json")["token"] = Json(f"gpt/users/{user_id}.json").get("token", 0) + count
                        await send_text("chatgpt.buy_success", [count], user_id)
                    else:
                        await send_text("currency.no_money", [0.04 * count], user_id)
                    await matcher.finish()
            case _:
                if not check_user_tokens(user_id):
                    await matcher.finish(lang.text("chatgpt.no_enough_token", [], user_id))
                session_id = get_user_session(user_id)
                session = get_session_by_id(session_id)
                if session["is_locked"]:
                    await matcher.finish(lang.text("chatgpt.session_locked", [session_id], user_id))
                session["is_locked"] = True
                add_message_to_session(session_id, "user", " ".join(argv))
                reply = await get_chatgpt_reply(get_session_messages(session_id))
                session["is_locked"] = False
                add_message_to_session(session_id, reply["choices"][0]["message"]["role"], reply["choices"][0]["message"]["content"])
                await matcher.finish(generate_gpt_reply(
                    reply["choices"][0]["message"]["content"],
                    reduce_tokens(user_id, reply["usage"]["total_tokens"]),
                    user_id
                ), at_sender=True)



    except BaseException:
        await error.report()
