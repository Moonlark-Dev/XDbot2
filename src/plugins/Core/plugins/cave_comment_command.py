from ._utils import *
from .cave import showEula

# @on_command("cave-c", aliases={"cave-comment"}).handle()

@command("cave-c", aliases={"cave-comment"})
async def handle_cave_comment_command(bot: Bot, event: MessageEvent, message: Message):
    await showEula(event.get_user_id())
    if str(event.user_id) in json.load(open("data/cave.banned.json", encoding="utf-8")):
            await finish("cave.cannot_comment", [], str(event.user_id))
    send_text("cave.test")
    cave_id = int(message.extract_plain_text().split(" ")[0])

