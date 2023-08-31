from ._utils import *
import asyncio
from .duel.contingent import Contingent
from .duel.monomer import Monomer
from .duel.scheduler import Scheduler

duel_requests = {}


@create_group_command("duel")
async def handle_duel_command(bot, event: GroupMessageEvent, message: Message) -> None:
    passive_qq = int(str(message).replace("[CQ:at,qq=", "").replace("]", "").strip())
    duel_requests[passive_qq] = {
        "accepted": False,
        "active": event.user_id,
        "group_id": event.group_id,
    }
    await send_text("duel.duel_request", [passive_qq, event.user_id], passive_qq)
    # 过期后删除


async def init_monomer(bot: Bot, user_id: int) -> Monomer:
    return Monomer(
        Json(f"duel/u{user_id}.json").get("weapons", "leather_case"),
        Json(f"duel/u{user_id}.json").get("relics", {}),
        Json(f"duel/u{user_id}.json").get("ball", "leather_case"),
        100,
        (await bot.get_stranger_info(user_id=user_id))["nickname"],
    )


async def init_duel(bot: Bot, active_user_id: int, passive_user_id: int) -> Scheduler:
    active_contingent = Contingent([await init_monomer(bot, active_user_id)])
    passive_contingent = Contingent([await init_monomer(bot, passive_user_id)])
    active_contingent.enemy = passive_contingent
    passive_contingent.enemy = active_contingent
    return Scheduler(active_contingent, passive_contingent)


def parse_result_node_messages(bot: Bot, scheduler: Scheduler):
    loggers = scheduler.controller.logs
    node_messages = []
    for log in loggers:
        node_messages.append(
            {
                "type": "node",
                "data": {"uin": bot.self_id, "nickname": "XDbot2 Duel", "content": log.replace("[", "\\[")},
            }
        )
    return node_messages


@create_group_command("duel-accept")
async def handle_duel_command(bot, event: GroupMessageEvent, message: Message):
    if event.user_id not in duel_requests.keys():
        await finish("duel.no_request", [], event.user_id)
    if event.group_id != duel_requests[event.user_id]["group_id"]:
        await finish("duel.no_request", [], event.user_id)
    if duel_requests[event.user_id]["accepted"]:
        await finish("duel.no_request", [], event.user_id)
    duel_requests[event.user_id]["accepted"] = True
    # TODO 检查是否装备装备
    scheduler = await init_duel(
        bot, duel_requests[event.user_id]["active"], event.user_id
    )
    scheduler.start_fighting()
    await bot.call_api(
        "send_group_forward_msg",
        group_id=event.group_id,
        messages=parse_result_node_messages(bot, scheduler),
    )
