from ._utils import *
from .duel.monomer import load_json, Monomer


def get_user_equip(user_id: int, _type: str = "weapons") -> dict:
    equip = Json(f"duel/u{user_id}.json").get(_type, "leather_case")
    return load_json(f"kits/{equip}.json")


def get_weakness(user_id: int) -> str:
    monomer = Monomer(
        Json(f"duel/u{user_id}.json").get("weapons", "leather_case"),
        Json(f"duel/u{user_id}.json").get("relics", {}),
        Json(f"duel/u{user_id}.json").get("ball", "leather_case"),
        100,
        f"u{user_id}",
    )
    return " ".join(monomer.get_weakness())


async def show_equip(event: MessageEvent, argv: list[str]) -> None:
    match get_list_item(argv, 1, ""):
        case "":
            weapon_kit_data = get_user_equip(event.user_id, "weapons")
            ball_kit_data = get_user_equip(event.user_id, "ball")
            await finish(
                "duel_equip.show_euqip",
                [
                    event.user_id,
                    weapon_kit_data["weapons"]["name"],
                    weapon_kit_data["level"],
                    # 遗器（保留位置）
                    ball_kit_data["ball"]["name"],
                    ball_kit_data["level"],
                    get_weakness(),
                ],
                event.user_id,
                False,
                True,
            )


@create_command("duel-equip", aliases={"duel-e", "装备"})
async def duel_equip_command(bot: Bot, event: MessageEvent, message: Message):
    argv = message.extract_plain_text().split(" ")
    match argv[0]:
        case "" | "view":
            await show_equip(event, argv)
