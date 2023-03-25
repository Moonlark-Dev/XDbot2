from nonebot import on_command
from nonebot.permission import SUPERUSER

su = on_command("su", aliases={"超管"}, permission=SUPERUSER)
