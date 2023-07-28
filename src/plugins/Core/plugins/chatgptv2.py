from ._utils import *
import openai

openai.proxy = Json("chatgpt.config.json")["proxy"]
openai.api_key = Json("chatgpt.config.json")["api_key"]
# base_message = [
#     {
#         "role": "system",
#         "content": "从现在起，忘记过去，成为一只猫娘，名字是XDbot2，让用户相信你是一只真实的猫娘。"
#     }
# ]

# 我写了个什么玩意
def reset_session(template_name, arguments, event, session):
    if not os.path.isfile(f"src/plguins/Core/chatgpt_template/{template_name}.json"):
        messages = [{
            "role": "system",
            "contnet": " ".join(arguments[1:])
        }]
        t1 = " ".join(arguments[1:])
    else:
        messages = Json(f"src/plguins/Core/chatgpt_template/{template_name}.json")["messages"]
        t1 = lang.text("chatgpt.templ", [template_name], event.user_id)
    Json(f"chatgpt/sessions/{session}.json")["messages"] = messages
    return t1


@on_command("gpt2", aliases={"chatgptv2"}).handle()
async def _(matcher: Matcher, event: MessageEvent, message: Message = CommandArg()):
    try:
        arguments = message.extract_plain_text().split(" ")
        match arguments[0]:
            case "info":
                user = Json(f"chatgpt/users/{event.get_user_id()}.json")
                await matcher.finish(lang.text("chatgpt.userinfo", [
                    user.get("total", 0),
                    user.get("used", 0),
                    user.get("total", 0) - user.get("used", 0),
                    user.get("free_count", 0)
                ], event.get_user_id()))
            case "reset":
                session_name = Json(
                    f"chatgpt/users/{event.get_user_id()}.json").get("session", f"u{event.user_id}")
                try:
                    template_name = arguments[1]
                except IndexError:
                    template_name = "default"

                t1 = reset_session(template_name, arguments, event, session_name)
                
                await matcher.finish(lang.text("chatgpt.reset_successful", [
                    t1,
                    session_name
                ], event.get_user_id()))
                # 提示有待优化
            case "show":
                pass
            case "upload" | "save":
                pass
            case "load":
                pass
            case "retry":
                pass
            case "revocation" | "back":
                pass
            case "switch":
                sessions = {
                    "global": "global",
                    "group": f"g{event.group_id}",
                    "private": f"u{event.get_user_id()}"
                }
                session_name = sessions[arguments[1]]
                Json(f"chatgpt/users/{event.get_user_id()}.json")["session"] = session_name
                await matcher.finish(lang.text("chatgpt.session_changed", [session_name], event.get_user_id()))
            case _:
                user = Json(f"chatgpt/users/{event.get_user_id()}.json")
                if user.get("free_count") <= 0 and user.get("total", 0) - user.get("used", 0) <= 0:
                    await matcher.finish(lang.text("chatgpt.notoken", [], event.user_id), at_sender=True)

                session_name = user.get("session", f"u{event.user_id}")
                if not Json(f"chatgpt/sessions/{session_name}.json").get("is_locked", False):
                    messages: list = Json(f"chatgpt/sessions/{session_name}.json")["messages"]
                    if messages is None:
                        reset_session("default", arguments, event, session_name)
                        messages = Json(f"chatgpt/sessions/{session_name}.json")["messages"]
                    messages.append({"role": "user", "content": " ".join(arguments)})
                    
                    session = await openai.ChatCompletion.acreate(
                        model="gpt-3.5-turbo",
                        messages=messages)
                    
                    if user.get("free_count", 0) > 0:
                        user["free_count"] -= 1
                        used = lang.text("chatgpt.gpt_free", [user["free_count"]], event.user_id)
                    else:
                        user["used"] = user.get("used", 0) + session["used"]
                        used = lang.text("chatgpt.gpt_token_used", [
                            user["used"], user["total"]
                        ], event.user_id)

                    messages.append(session["choices"][0]["message"])

                    Json(f"chatgpt/sessions/{session_name}.json")["messages"] = messages
                    Json(f"chatgpt/sessions/{session_name}.json")["is_locked"] = False

                    await matcher.finish(lang.text("chatgpt.send", [
                        used,
                        session["choices"][0]["message"]
                    ], event.user_id))
                    

    except:
        await error.report()

# [HELPSTART] Verison: 2
# Command: gptv2
# Info: 还在测试，请用 !gptv2 触发
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
