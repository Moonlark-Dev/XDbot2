from nonebot.rule import Rule
from nonebot.adapters.onebot.v11 import GroupMessageEvent

from ._onebot import GroupID


def group(group_id: GroupID):
    def wapper(event: GroupMessageEvent):
        return event.group_id == int(group_id)
    return Rule(wapper)
