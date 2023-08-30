from ._utils import *
from .cave import showEula

# @on_command("cave-c", aliases={"cave-comment"}).handle()

@create_command("cave-c", aliases={"cave-comment"})
async def handle_cave_comment_command(bot: Bot, event: MessageEvent, message: Message):
    await showEula(event.get_user_id())
    if str(event.user_id) in json.load(open("data/cave.banned.json", encoding="utf-8")):
        await finish("cave.cannot_comment", [], str(event.user_id))
    try:
        cave_id = int(message.extract_plain_text().split(" ")[0])
    except IndexError:
        await finish("currency.wrong_argv", ["cave"], event.user_id, False, True)
    except ValueError:
        await finish("cave.notfound", [message.extract_plain_text().split(" ")[0]], event.user_id, False, True)
    cave_comments = json.load(open("data/cave.comments.json", encoding="utf-8"))
    if cave_id not in cave_comments.keys():
            cave_comments[cave_id] = {"count": 1, "data": {}}
    cave_comments[cave_id]["data"][str(cave_comments[cave_id]["count"])] = {
        "id": cave_comments[cave_id]["count"],
        "text": (comment_text := " ".join(str(message).split(" ")[1:])),
        "sender": event.get_user_id(),
    }
    cave_comments[cave_id]["count"] += 1
    json.dump(cave_comments, open("data/cave.comments.json", "w", encoding="utf-8"))
    await error.report((
        f"「新回声洞评论（{cave_id}#{cave_comments[cave_id]['count'] - 1}）」\n"
        f"{comment_text}\n"
        f"{event.get_session_id()}"
    ), feedback=False)