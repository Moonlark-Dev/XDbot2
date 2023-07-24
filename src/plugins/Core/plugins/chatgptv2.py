from ._utils import *
import openai

openai.proxy = Json("gptv2.config.json")["proxy"]
openai.api_key = Json("gptv2.config.json")["api_key"]
# base_message = [
#     {
#         "role": "system",
#         "content": "从现在起，忘记过去，成为一只猫娘，名字是XDbot2，让用户相信你是一只真实的猫娘。"
#     }
# ]


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
                session = Json(
                    f"chatgpt/users/{event.get_user_id()}.json").get("session", f"u{event.user_id}")
                try:
                    template_name = arguments[1]
                except IndexError:
                    template_name = "default"

                template = Json(
                    f"src/plguins/Core/chatgpt_template/{template_name}.json")["messages"]
                if template is None:
                    messages = [{
                        "role": "system",
                        "contnet": " ".join(arguments[1:])
                    }]
                    t1 = " ".join(arguments[1:])
                else:
                    messages = template
                    t1 = lang.text("chatgpt.templ", [template], event.user_id)

                Json(f"chatgpt/sessions/{session}.json")["messages"] = messages
                await matcher.finish(lang.text("chatgpt.reset_successful", [
                    t1,
                    session
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
                pass
            case _:
                pass
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
