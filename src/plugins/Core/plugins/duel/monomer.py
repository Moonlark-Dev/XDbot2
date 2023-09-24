import json
import os.path
import random

from . import path
from .contingent import Contingent
from .controller import Controller

SKIP = False


def load_json(name: str) -> dict:
    return json.load(
        open(
            os.path.join(
                path.res_path, name.replace("leathcer_case.json", "leather_case.json")
            ),
            encoding="utf-8",
        )
    )


def get_base_properties(_type: str = "primary") -> dict:
    return load_json(f"base_properties/{_type}.json")


class Monomer:
    def __init__(
        self,
        weapons: str,
        relics: dict[str, dict],
        ball: str,
        hp: int,
        name: str,
        weapons_level: int = 1,
        ball_level: int = 1,
    ) -> None:
        base_properties = get_base_properties()
        self._default_data = base_properties.copy()
        self.gain_list = []
        self.triggers = {}
        self.buff = {}
        self.toughness_strips = 100
        self.hp = hp
        self.name = name
        self.energy = 20
        self.paused_effect = []

        self.contingent: Contingent
        self.controller: Controller
        self.latest_attacked_monomer: Monomer
        self.reduced_action_value: float = 0.0
        self.shield = 0

        self.get_weapons(weapons, weapons_level)
        self.get_ball(ball, ball_level)
        self.get_relics_gain(relics)
        self.get_kit_gain()

        self._default_data = self.parse_gain(self.gain_list)
        self.data = self._default_data.copy()
        del self.gain_list

    def set_controller(self, controller: Controller):
        self.controller = controller

    def add_enegy(self, count: int):
        self.energy += count * (1 + self.data["charging_efficiency"])
        self.energy = min(100, self.energy)

    def get_kits(self) -> dict:
        kits = {}
        for relics_item in self.relics:
            kits[relics_item] = kits.get(relics_item, 0) + 1
        kits[self.weapons["kit"]] = kits.get(self.weapons["kit"], 0) + 1
        kits[self.ball["kit"]] = kits.get(self.ball["kit"], 0) + 1
        return kits

    def set_contingent(self, contingent):
        self.contingent = contingent

    def get_kit_gain(self) -> None:
        for kit, count in list(self.get_kits().items()):
            if count >= 2:
                self.gain_list += list(
                    load_json(f"kits/{kit}.json")["kit_effect"]["2"]
                    .get("gain", {})
                    .items()
                )
            if count >= 4:
                self.gain_list += list(
                    load_json(f"kits/{kit}.json")["kit_effect"]["4"]
                    .get("gain", {})
                    .items()
                )
            if count >= 6:
                self.gain_list += list(
                    load_json(f"kits/{kit}.json")["kit_effect"]["6"]
                    .get("gain", {})
                    .items()
                )
            if self.ball["kit"] == self.weapons["kit"]:
                self.gain_list += list(
                    load_json(f"kits/{kit}.json")["kit_effect"]["resonance"]
                    .get("gain", {})
                    .items()
                )

    def prepare_before_other_action(self):
        if self.has_buff("freezing"):
            self.controller.add_logger(f"[{self.name}]: 你被冻结了，无法行动！\n")
            return
        if self.energy >= 100:
            self.energy = 0
            self.controller.add_logger(
                f'[{self.name}]: 发动了终结技 <{self.ball["skill"]["name"]}>\n'
            )
            self.parse_effect(self.ball["skill"]["effect"])

    def start_action(self):
        self.run_tigger("action.start")
        if (
            self.weapons["skill"]["type"] == "treat"
            and (self.hp / self.data["health"]) <= 0.3
        ):  # 治疗型
            _type = "skill"
        elif (
            self.weapons["skill"]["type"] != "treat"
            and random.random() <= (self.contingent.battle_skill_points / 5) ** 2
        ):
            _type = "skill"
        elif self.contingent.battle_skill_points == 0:
            _type = "primary"
        else:
            _type = "primary"
        if _type == "skill":
            self.contingent.battle_skill_points -= 1
            if "attack" in self.weapons["skill"].keys():
                self.make_attack(
                    (data := self.weapons["skill"]["attack"])["type"],
                    data["value"],
                    self.weapons["element"],
                )
                self.controller.add_logger(
                    f'[{self.name}]: 使用了 <{self.weapons["skill"]["name"]}>\n'
                )
            if "effect" in self.weapons["skill"].keys():
                self.parse_effect(self.weapons["skill"]["effect"])
            self.run_tigger("our.used_skill")
            self.add_enegy(30)
        else:
            self.contingent.battle_skill_points += 1
            self.make_attack(
                (data := self.weapons["attack"])["type"],
                data["value"],
                self.weapons["element"],
            )
            self.add_enegy(20)
            self.controller.add_logger(f"[{self.name}]: 使用了 <普通攻击>\n")

    def make_attack(self, _type: str, value: float, attribute: str):
        if _type in ["single", "diffusion"]:
            target = self.get_lowest_hp_monomer(self.contingent.enemy)
            self.latest_attacked_monomer = target
            if _type == "diffusion":
                if (_tmp_pos := self.contingent.enemy.monomers.index(target)) > 0:
                    self.contingent.enemy.monomers[_tmp_pos - 1].attacked(
                        self.get_harm(value) * 0.25, attribute, self
                    )
                if _tmp_pos != len(self.contingent.enemy.monomers) - 1:
                    self.contingent.enemy.monomers[_tmp_pos + 1].attacked(
                        self.get_harm(value), attribute, self
                    )
            target.attacked(self.get_harm(value), attribute, self)
        elif _type == "random":
            for i in range(5):
                try:
                    self.latest_attacked_monomer = random.choice(
                        self.contingent.enemy.monomers
                    )
                except IndexError:
                    break
                self.latest_attacked_monomer.attacked(
                    self.get_harm(value), attribute, self
                )
        self.contingent.run_tigger("our.hit.enemy")

    def get_harm(self, value: float):
        return (
            self.data["attack"]
            * value
            * (
                (1 + self.data["cirtical_damage"])
                if random.random() <= self.data["cirtical_strike_chance"]
                else 1
            )
        )

    def get_weapons(self, weapons: str, level: int) -> None:
        self.weapons = self.parse_level_data(
            load_json(f"kits/{weapons}.json")["weapons"], level
        )
        self.weapons["kit"] = weapons
        if "gain" in self.weapons.keys():
            self.gain_list += list(self.weapons["gain"].items())

    def parse_level_data(self, data: dict[str, any], level: int = 1) -> dict:
        _data = data.copy()
        for key, value in list(_data.items()):
            if isinstance(value, list) and len(value) == 5:
                _data[key] = value[level - 1]
            elif isinstance(value, dict):
                _data[key] = self.parse_level_data(value, level)
            elif isinstance(value, list):
                for i in range(len(value)):
                    if isinstance(value[i], dict):
                        value[i] = self.parse_level_data(value[i], level)
        return _data

    def get_ball(self, ball: str, level: int) -> None:
        self.ball = self.parse_level_data(load_json(f"kits/{ball}.json")["ball"], level)
        self.ball["kit"] = ball
        if "gain" in self.ball.keys():
            self.gain_list += list(self.ball["gain"].items())

    def get_relics_gain(self, relics: dict[str, dict]) -> None:
        self.relics = []
        for relics_item in list(relics.values()):
            self.relics.append(relics_item["kit"])
            self.gain_list += list(relics_item["gain"].items())

    def parse_gain(self, gain_list: list[tuple], base: dict | None = None) -> dict:
        default_data = base or self._default_data.copy()
        percentage_gain = {}
        for gain_name, value in gain_list:
            if isinstance(value, float):
                percentage_gain[gain_name] = percentage_gain.get(gain_name, 0.0) + value
            else:
                default_data[gain_name] = default_data.get(gain_name, 0) + value
        _default_data = default_data.copy()
        for key, value in list(percentage_gain.items()):
            default_data[key] = _default_data.get(key, 0) * (1 + value)
        return default_data

    def effect_add_hp(self, effect: dict) -> None:
        if isinstance(effect["value"], float):
            self.hp += self.data["health"] * (
                effect["value"] + self.data["therapeutic_volume_bonus"]
            )
        else:
            self.hp += effect["value"] * (1 + self.data["therapeutic_volume_bonus"])
        self.hp = min(self.hp, self.data["health"])

    def effect_add_trigger(self, effect: dict):
        if effect["condition"] not in self.triggers.keys():
            self.triggers[effect["condition"]] = []
        self.triggers[effect["condition"]].append(effect["effect"])

    def effect_add_battle_skill_points(self, effect: dict) -> None:
        if effect["target"]:
            if self.contingent.enemy.battle_skill_points < 5:
                self.contingent.enemy.battle_skill_points += 1
        elif self.contingent.battle_skill_points < 5:
            self.contingent.battle_skill_points += 1

    def effect_remove_battle_skill_points(self, effect: dict) -> None:
        if effect["target"]:
            if self.contingent.enemy.battle_skill_points > 0:
                self.contingent.enemy.battle_skill_points -= 1
        elif self.contingent.enemy.battle_skill_points > 0:
            self.contingent.enemy.battle_skill_points -= 1

    def prepare_before_fighting(self) -> None:
        self.run_tigger("fighting.start")

    def run_tigger(self, event: str) -> None:
        try:
            for effect in self.triggers[event]:
                self.parse_effect(effect)
        except KeyError:
            pass

    def parse_effect(self, effect_block: list[dict]) -> None:
        for effect in effect_block:
            match effect["function"]:
                case "add_hp":
                    self.effect_add_hp(effect)
                case "add_trigger":
                    self.effect_add_trigger(effect)
                case "verify_probabilities":
                    if random.random() > effect["probability"]:
                        break
                case "add_battle_skill_points":
                    self.effect_add_battle_skill_points(effect)
                case "remove_battle_skill_points":
                    self.effect_remove_battle_skill_points(effect)
                case "add_buff":
                    self.effect_add_buff(effect)
                case "add_shield":
                    self.shield += (
                        self.data[effect["thickness"]["base"]]
                        * effect["thickness"]["value"]
                    )
                case "make_attack":
                    self.effect_make_attack(effect)
                case "update_gain":
                    self.data = self.parse_gain(effect["gain"])
                case "wait_action":
                    self.paused_effect.append({
                        "type": "action",
                        "count": effect["count"],
                        "effect": effect["effect"]
                    })
                case "restore_energy":
                    self.add_enegy(effect["value"])

    def effect_make_attack(self, effect: dict):
        self.controller.add_logger(f"[{self.name}]: 使用了 <{effect['name']}>\n")
        self.make_attack(
            effect["attack"]["type"], effect["attack"]["value"], effect["element"]
        )

    def effect_add_buff(self, effect: dict) -> None:
        match effect["target"]:
            case 0:
                match effect["range"]:
                    case 0:
                        self.add_buff(
                            effect["buff"],
                            effect["cling"],
                            effect["data"],
                            effect["probability"],
                            self,
                        )
                    case 1:
                        self.get_lowest_hp_monomer(self.contingent).add_buff(
                            effect["buff"],
                            effect["cling"],
                            effect["data"],
                            effect["probability"],
                            self,
                        )
                    case 2:
                        for i in self.contingent.monomers:
                            monomer = self.contingent.monomers[i]
                            monomer.add_buff(
                                effect["buff"],
                                effect["cling"],
                                effect["data"],
                                effect["probability"],
                                self,
                            )

            case 1:
                match effect["range"]:
                    case 0:
                        self.latest_attacked_monomer.add_buff(
                            effect["buff"],
                            effect["cling"],
                            effect["data"],
                            effect["probability"],
                            self,
                        )
                    case 1:
                        try:
                            _tmp_monomers = [self.latest_attacked_monomer]
                            if (
                                _tmp_pos := self.contingent.enemy.monomers.index(
                                    self.latest_attacked_monomer
                                )
                            ) > 0:
                                _tmp_monomers.append(
                                    self.contingent.enemy.monomers[_tmp_pos - 1]
                                )
                            if _tmp_pos != len(self.contingent.enemy.monomers) - 1:
                                _tmp_monomers.append(
                                    self.contingent.enemy.monomers[_tmp_pos + 1]
                                )
                            for i in range(len(_tmp_monomers)):
                                _tmp_monomers[i].add_buff(
                                    effect["buff"],
                                    effect["cling"],
                                    effect["data"],
                                    effect["probability"],
                                    self,
                                )
                        except IndexError:
                            pass
                        except ValueError:
                            pass
                    case 2:
                        self.get_lowest_hp_monomer(self.contingent.enemy).add_buff(
                            effect["buff"],
                            effect["cling"],
                            effect["data"],
                            effect["probability"],
                            self,
                        )
                    case 3:
                        random.choice(self.contingent.enemy.monomers).add_buff(
                            effect["buff"],
                            effect["cling"],
                            effect["data"],
                            effect["probability"],
                            self,
                        )
                    case 4:
                        for i in self.contingent.enemy.monomers:
                            self.contingent.enemy.monomers[i].add_buff(
                                effect["buff"],
                                effect["cling"],
                                effect["data"],
                                effect["probability"],
                                self,
                            )

    @staticmethod
    def get_lowest_hp_monomer(base: Contingent):
        lowest_hp_monomer: Monomer = base.monomers[0]
        for i in range(len(base.monomers)):
            if base.monomers[i].hp <= lowest_hp_monomer.hp:
                lowest_hp_monomer = base.monomers[i]
        return lowest_hp_monomer

    def add_buff(
        self, buff: str, cling: int, data: dict, probability: float, from_monomer
    ):
        if load_json(f"buff/{buff}.json")[
            "negative"
        ] and random.random() > self.get_hit_probability(probability, from_monomer):
            return
        if buff in self.buff.keys():
            self.buff[buff]["cling"] += cling
            self.buff[buff]["data"].update(data)
        else:
            self.buff[buff] = {
                "cling": cling,
                "negative": load_json(f"buff/{buff}.json")["negative"],
                "data": data,
            }
        self.controller.add_logger(f"[{self.name}]: 被赋予 buff：{buff}\n")

    def get_hit_probability(self, basic_probability: float, from_monomer):
        return (
            basic_probability
            * (1 + from_monomer.data["effect_hit"])
            * (1 - self.data["effect_resistance"])
        )

    def get_action_value(self):
        return 10000 / self.data["speed"] - self.reduced_action_value

    def reduce_action_value(self, count: int):
        self.reduced_action_value += count

    def run_buff_effect(self):
        for buff_name in list(self.buff.keys()):
            buff_data = self.buff[buff_name]
            buff_data["cling"] -= 1
            match buff_name:
                case "freezing":
                    self.attacked(15 if buff_data["cling"] == 0 else 10, "冰", None)
                case "burn":
                    self.attacked(17, "火", None)
            if buff_data["cling"] == 0:
                self.buff.pop(buff_name)

    def attacked(self, harm: float, attribute: str, from_monomer):
        self.run_tigger("our.attacked")
        if (
            self.toughness_strips > 0
            and attribute in self.get_weakness()
            and not self.shield
        ):
            self.toughness_strips -= 15 * from_monomer.data["elemental_mastery"]
        if self.toughness_strips > 0:
            harm *= 0.8 if attribute in self.get_weakness() else 0.9
            harm *= 1 - min(0.75, self.data["defense"] / 2)
        if self.shield >= harm:
            self.shield -= harm
            harm = 0
        else:
            harm -= self.shield
            self.shield = 0
        self.hp -= 1 if self.data.get("fatal_injury_protection", False) else harm
        self.data["fatal_injury_protection"] = False
        if self.hp <= 0:
            self._hp = self.hp
            self.hp = 0
            self.run_tigger("our.died")
            self.contingent.died(self)
        self.add_enegy(10)

    def get_weakness(self):
        weakness = set()
        for relics in self.relics:
            weakness.add(load_json(f"kits/{relics}")["weakness"])
        return list(weakness)

    def has_buff(self, buff_name: str):
        return buff_name in self.buff.keys()

    def prepare_before_action(self) -> bool:
        self.run_tigger("action.start")
        paused_effect_needed_remove = []
        for i in range(len(self.paused_effect)):
            if self.paused_effect[i]["type"] == "action":
                self.paused_effect[i]["count"] -= 1
                if self.paused_effect[i]["count"] <= 0:
                    self.parse_effect(self.paused_effect[i]["count"])
                    paused_effect_needed_remove.append(i - len(paused_effect_needed_remove))
        for length in paused_effect_needed_remove:
            self.paused_effect.pop(length)
        self.run_buff_effect()
        if self.has_buff("freezing"):
            self.controller.add_logger(f"[{self.name}]: 你被冻结了，无法行动！\n")
            return SKIP

    def prepare_before_the_round(self) -> None:
        self.run_tigger("round.start")
