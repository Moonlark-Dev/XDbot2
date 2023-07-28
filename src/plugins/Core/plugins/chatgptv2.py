
from ._utils import *
import openai

openai.proxy = Json("chatgpt.config.json")["proxy"]
openai.api_key = Json("chatgpt.config.json")["api_key"]

# [HELPSTART] Version: 2
# Command: gpt2
# Info: 还在测试，请用 !gpt2 触发
# Usage: gpt info
# Usage: gpt reset [模板]
# Usage: gpt show [会话ID]
# Usage: gpt load <会话永久ID>
# Usage: gpt upload [会话ID]
# Usage: gpt retry
# Usage: gpt back
# Usage: gpt switch {global|group|private}
# Usage: gpt token buy <数量>
# [HELPEND]

def get_user_info(user_id: str) -> str:
    user_data = Json(f"gpt/users/{user_id}.json")
    return lang.text("chatgpt.user_info", [
        user_data["tokens"],
        user_data["free"]
    ], user_id)


def init_session(session_name: str, system_message: str | None, force_unlock: bool = False) -> bool:
    if force_unlock:
        Json(f"gpt/sessions/{session_name}.json")["is_locked"] = False
    if Json(f"gpt/sessions/{session_name}.json")["is_locked"]:
        return ERROR
    if system_message is not None:
        Json(f"gpt/sessions/{session_name}.json")["messages"] = []
    else:
        Json(f"gpt/sessions/{session_name}.json")["messages"] = [{
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


def reset_session(session_name: str, template: str | None = None, force_unlock: bool = False, _system_message: str | None = None) -> bool:
    system_message = get_template_by_name(template) or _system_message
    return init_session(session_name, system_message, force_unlock)



def get_user_session(user_id: str) -> str:
    return Json(f"gpt/users/{user_id}.json")["session"] or f"u{user_id}"


def change_session(user_id: str, session: str) -> None:
    Json(f"gpt/users/{user_id}.json")["session"] = session


@on_command("gpt2").handle()
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
            
                

    except BaseException:
        await error.report()
