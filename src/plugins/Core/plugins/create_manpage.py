# [DEVELOP]
from ._utils import *
import os
from .chatgptv2 import get_chatgpt_reply


async def get_command_help(command_name: str, user_id: int) -> dict | None:
    if (data := Json("help.json")[command_name]) is not None:
        return data
    await finish("create_manpage.404", [], user_id, False, True)


def generate_prompt(command_help: dict) -> str:
    prompt = """请参考以下指令帮助，写一个指令文档，需要包含名称、描述、权限、用法、示例（不包含输出示例）等信息，示例如下：

```markdown
# 指令帮助 —— <命令名>

## 描述：
...

### 权限：

- `everyone`

## 用法

### `<用法1（如 calc <表达式>）>`

- 说明：<用法说明>
- 示例：`<用法示例>`

### `<用法二>`

- 说明：<用法说明>
- 示例：`<用法示例>`


本 ManPage 使用 ChatGPT-3.5-Turbo 生成
```

用法示例需要添加指令前缀`/`

替换`<...>`时需要将`<`和`>`一并替换

命令帮助如下：
"""
    prompt += (
        f"命令名：{command_help['name']}\n"
        f"简介（[...]内为权限，以*开头（需要去掉*），使用空格分割，没有则为 *everyone）：{command_help['info']}\n"
        "所有用法（<...>为必要参数，[...]为可选参数，{...|...}为选择参数）："
    )
    for usage in command_help["usage"]:
        prompt += f"- {usage}"
    return prompt


def push_changes(command_name) -> str:
    os.system("git add -A")
    os.system(f"git commit -a -m \"[add] Create manpage for {command_name}\"")
    return os.popen("git push").read()


@create_command("create-manpage")
async def create_manpage(_bot: Bot, event: MessageEvent, message: Message, matcher: Matcher = Matcher()):
    session = await get_chatgpt_reply([{
        "role": "user",
        "content": generate_prompt(await get_command_help(message.extract_plain_text(), event.user_id))
    }])
    await matcher.send(session["choices"][0]["message"]["content"])
    try:
        os.mkdir(f"docs/{message.extract_plain_text()}")
    except OSError:
        pass
    with open(path := f"docs/{message.extract_plain_text()}/0.md", "w", encoding="utf-8") as f:
        f.write(session["choices"][0]["message"]["content"])
    await send_text("create_manpage.saved", [path], event.user_id)
    await matcher.send(push_changes(message.extract_plain_text()))
