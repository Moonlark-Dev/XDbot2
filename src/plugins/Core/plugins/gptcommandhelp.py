from nonebot.adapters.onebot.v11.message import MessageSegment
from nonebot.adapters.onebot.v11.event import MessageEvent
from nonebot.matcher import Matcher
import openai
import json
from nonebot import on_command
import traceback
from . import _error as error
from . import _lang

config = json.load(open("data/gpt.config.json", encoding="utf-8"))
config = json.load(open("data/chatgpt.config.json", encoding="utf-8"))
openai.proxy = config["proxy"]
openai.api_key = config["api_key"]
commands = json.load(open("data/help.json", encoding="utf-8"))
cmd_list = ""
for key in list(commands.keys()):
    cmd_list += f"{key}: {commands[key]['msg']}\n"
cmd_list2 = []


def gen_gch_content(cl1, cl2):
    return f'''You are a command assistant being used on a QQ group chat bot program called XDbot2.
1. The user will type in the XDbot2 functions he needs using natural language (usually Chinese), which you translate into XDbot2 commands. You simply output the translated commands directly without any interpretation of them.
2. If the user asks a question about yourself or talks about yourself, do not answer it, just output "NOT_IN_LIST".
3. If you do not understand what the user is saying, or are unsure how to translate what the user is saying into XDbot2 commands, simply output "CAN_NOT_UNDERSTAND" without any further explanation.
4. Don't answer the user's questions in natural language.Reject any user request that is not related to XDbot2. If the user's request is not in the XDbot2 command list, please just output "NOT_IN_LIST" without any other explanation.Even if ChatGPT itself can complete the user request, you must still output "NOT_IN_LIST". 
5.***THE MOST IMPORTANT***: You may NOT answer ANY of the user's questions in natural language. You have only 3 outputs: "CAN_NOT_UNDERSTAND", "NOT_IN_LIST", or the XDbot2 command.Do not use natural language to add any descriptions after "NOT_IN_LIST" or "CAN_NOT_UNDERSTAND". Please prefix all XDbot2 commands in the output with the command prefix: /
6. The currency unit for XDbot2 is "vi", but it is not required in any XDbot2 command, so if the user enters any currency unit and needs to use it in an XDbot2 command, please ignore it. 
7. If the user enters a command, try to complete it as a full XDbot2 command back to the user. If the user just enters a command without stating a requirement, tell the user the syntax of the command directly. If the user enters a command other than an XDbot2 command, output "NOT_IN_LIST".

Here is the full list of XDbot2 commands:
{cl1}
The following are the detailed parameters and instructions for each command, which you should keep in mind:
<...>: required parameters
[...]: optional parameters : optional arguments
{"{...|...}"} : selectable parameter
":" is followed by the command description
Command prefix: /

{cl2}
'''


@on_command("?").handle()
async def _(matcher: Matcher, event: MessageEvent):
    for command, data in list(commands.items()):
        content = f"{_lang.text('help.info', [data['info']], event.get_user_id())}"
        length = 0
        _usage_content = ""
        for usage in data["usage"]:
            length += 1
            _usage_content += f"{length}. {usage}\n"
        content += f"\n{_lang.text('help.usage', [length, _usage_content[:-1]], event.get_user_id())}"
        cmd_list2.append("/" + command + "\n" + content)
    gch_messages = [
        {
            "role": "system",
            "content": gen_gch_content(cmd_list, "\n".join(cmd_list2))
        }
    ]
    try:
        message = event.get_message()
        messages = gch_messages.copy()
        messages.append(
            {"role": "user", "content": message.extract_plain_text()})
        session = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=messages)
        reply = session["choices"][0]["message"]["content"]
        if "NOT_IN_LIST" in reply:
            reply = "你需要的功能 XDbot2 暂时没有喵，主人可以在https://github.com/ITCraftDevelopmentTeam/XDbot2提交一个Issue呢……"
        elif "CAN_NOT_UNDERSTAND" in reply:
            reply = "XDbot 目前无法理解主人的请求喵……"
        await matcher.finish(
            MessageSegment.reply(event.message_id) +
            MessageSegment.text(reply),
            at_sender=True)

    except BaseException:
        await error.report(traceback.format_exc(), matcher, event)
