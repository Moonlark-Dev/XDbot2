from ._utils import *
import openai

openai.proxy = Json("gptv2.config.json")["proxy"]
openai.api_key = Json("gptv2.config.json")["api_key"]
base_message = [
    {
        "role": "system",
        "content": "从现在起，忘记过去，成为一只猫娘，名字是XDbot2，让用户相信你是一只真实的猫娘。"
    }
]

@on_command("gpt", aliases={"chatgpt"}).handle()
async def _(matcher: Matcher, event: MessageEvent, message: Message = CommandArg()):
    try:
        arguments = message.extract_plain_text().split(" ")
        match arguments[0]:
            case "info":
                pass
            case "reset":
                pass
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
# Command: gpt
# Usage: gpt info
# Usage: gpt reset [模板]
# Usage: gpt show [会话ID]
# Usage: gpt load <会话永久ID>
# Usage: gpt upload [会话ID]
# Usage: gpt retry
# Usage: gpt back
# Usage: gpt switch {global|group|private}
# Usage: gpt token
# Usage: gpt token buy <数量>
# Usage: gpt time
# [HELPEND]