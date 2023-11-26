from ._utils import *
import asyncio
from .duel.contingent import Contingent
from .duel.monomer import Monomer
import time
import random
from .duel.scheduler import Scheduler
from nonebot_plugin_apscheduler import scheduler as nonebot_scheduler
from .etm.user import remove_hp, get_hp
from .etm.health import get_data
import os

duel_requests = {}


@nonebot_scheduler.scheduled_job(
    "cron", hour="0", minute="0", second="0", id="reset_force_duel_count"
)
async def reset_force_duel_count():
    for file in os.listdir("data/duel"):
        if file.startswith("u") and file.endswith(".json"):
            Json(f"duel/{file}")["force_duel_count"] = 0


@create_group_command("duel")
async def handle_duel_command(_bot, event: GroupMessageEvent, message: Message) -> None:
    passive_qq = int(str(message).replace("[CQ:at,qq=", "").replace("]", "").strip())
    duel_requests[passive_qq] = {
        "accepted": False,
        "active": event.user_id,
        "group_id": event.group_id,
        "time": (create_time := time.time()),
    }
    await send_text("duel.duel_request", [passive_qq, event.user_id], passive_qq)

    async def remove_data() -> None:
        await asyncio.sleep(180)
        if passive_qq not in duel_requests.keys():
            return
        if duel_requests["active"] != event.user_id:
            return
        if duel_requests["group_id"] != event.group_id:
            return
        if duel_requests["time"] != create_time:
            return
        duel_requests.pop(passive_qq)

    asyncio.create_task(remove_data())


async def init_monomer(bot: Bot, user_id: int) -> Monomer:
    return Monomer(
        Json(f"duel/u{user_id}.json").get("weapons", "leather_case"),
        Json(f"duel/u{user_id}.json").get("relics", {}),
        Json(f"duel/u{user_id}.json").get("ball", "leather_case"),
        get_hp(user_id),
        (await bot.get_stranger_info(user_id=user_id))["nickname"],
        Json(f"duel/u{user_id}.json").get("weapons_level", 1),
        Json(f"duel/u{user_id}.json").get("ball_level", 1),
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
                "data": {"uin": bot.self_id, "nickname": "XDbot2 Duel", "content": log},
            }
        )
    return node_messages


@create_group_command("duel-refuse")
async def handle_duel_refuse_command(_bot, event: GroupMessageEvent, _message: Message):
    if event.user_id not in duel_requests.keys():
        await finish("duel.no_request", [], event.user_id)
    if event.group_id != duel_requests[event.user_id]["group_id"]:
        await finish("duel.no_request", [], event.user_id)
    if duel_requests[event.user_id]["accepted"]:
        await finish("duel.no_request", [], event.user_id)
    duel_requests.pop(event.user_id)
    await finish("currency.ok", [], event.user_id)


# [HELPSTART] Version: 2
# Command: duel
# Msg: 决斗系统
# Info: 决斗系统（公开测试） [*group]
# Usage: duel-equip：查看装备
# Usage: duel <@用户>：发起决斗请求
# Usage: duel-accept：接受决斗请求
# Usage duel-refuse：拒绝决斗请求
# [HELPEND]


def get_hp_to_reduce(winner_id: int, is_active_win: bool) -> float:
    return get_data(winner_id, "health") * 0.85


@create_group_command("duel-force", {"kill"})
async def handle_force_duel(bot, event: GroupMessageEvent, message: Message):
    if Json(f"duel/u{event.user_id}.json").get("force_duel_count", 0) < 10:
        passive_user_id = int(str(message).replace("[CQ:at,qq=", "").replace("]", ""))
        # 后续考虑接入体力
        Json(f"duel/u{event.user_id}.json")["force_duel_count"] += 1
        scheduler = await init_duel(bot, event.user_id, passive_user_id)
        tmp = {
            False: [
                event.user_id,
                get_hp_to_reduce(passive_user_id, False),
                passive_user_id,
            ],
            True: [
                passive_user_id,
                get_hp_to_reduce(event.user_id, True),
                event.user_id,
            ],
        }[scheduler.start_fighting()]
        remove_hp(tmp[0], int(tmp[1]))
        # await bot.call_api(
        #     "send_group_forward_msg",
        #     group_id=event.group_id,
        #     messages=parse_result_node_messages(bot, scheduler),
        # )
        await finish("duel.result", [tmp[2]], event.user_id, False, parse_cq_code=True)


@create_group_command("duel-accept")
async def handle_duel_accept_command(
    bot, event: GroupMessageEvent, _message: Message
) -> None:
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
    tmp = {
        True: [event.user_id, duel_requests[event.user_id]["active"]],
        False: [duel_requests[event.user_id]["active"], event.user_id],
    }[scheduler.start_fighting()]
    remove_hp(tmp[0], get_data(tmp[0], "health") * 0.85)
    # await bot.call_api(
    #     "send_group_forward_msg",
    #     group_id=event.group_id,
    #     messages=parse_result_node_messages(bot, scheduler),
    # )
    await finish("duel.result", [tmp[1]], tmp[1], False, parse_cq_code=True)
