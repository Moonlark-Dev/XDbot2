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


def get_relics_info(relics_data: dict[str, dict], user_id: int) -> str:
    text = ""
    for _type, data in list(relics_data.items()):
        kit = data["kit"]
        text += lang.text("duel_equip.relics", [
            lang.text(f"duel_equip.relics_{_type}", [], user_id),
            load_json(f"kits/{kit}.json")["relics"][_type],
            data["level"]
        ])
        for gain in data["gain_list"]:
            text += lang.text("duel_equip.relics_gain", [
                gain["name"],
                data["value"] if isinstance(data["value"], int) else f"{data['value'] * 100}%"
            ])
    return text[:-1] + "\n"


async def show_equip(event: MessageEvent, argv: list[str]) -> None:
    match get_list_item(argv, 1, ""):
        case "":
            weapon_kit_data = get_user_equip(event.user_id, "weapons")
            ball_kit_data = get_user_equip(event.user_id, "ball")
            await finish(
                "duel_equip.show_equip",
                [
                    weapon_kit_data["weapons"]["name"],
                    Json(f"duel/u{event.user_id}.json").get("weapons_level", 1),
                    ball_kit_data["ball"]["name"],
                    Json(f"duel/u{event.user_id}.json").get("ball_level", 1),
                    get_relics_info(
                        Json(f"duel/u{event.user_id}.json").get("relics", {}), 
                        event.user_id
                    ),
                    "TODO"
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
