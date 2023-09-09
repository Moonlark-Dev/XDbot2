from .contingent import Contingent
from .round_boundaries import RoundBoundaries
from .monomer import Monomer, SKIP
from .controller import Controller


class Scheduler:
    def __init__(self, active: Contingent, passive: Contingent):
        self.active = active
        self.passive = passive
        self.controller = Controller()
        self.round_boundaries = RoundBoundaries()
        self.monomers: list[Monomer | RoundBoundaries] = (
            self.active.monomers + self.passive.monomers + [self.round_boundaries]
        )
        for i in range(len(self.monomers)):
            self.monomers[i].set_controller(self.controller)

    def start_fighting(self):
        self.prepare_fighting()
        while self.is_battle_ongoing():
            self.create_round_logger()
            self.start_round()

    def create_round_logger(self):
        self.controller.create_logger_block("======【回合开始】======\n")
        for i in range(len(self.monomers)):
            if not self.monomers[i].data.get("is_roundboundaries", False):
                self.controller.add_logger(
                    (
                        f"{self.monomers[i].name}:\n"
                        f"  HP: {self.monomers[i].hp}\n"
                        f"  Energy: {self.monomers[i].energy}\n"
                        f"  Shield: {self.monomers[i].shield}\n"
                    )
                )

    def start_round(self):
        self.prepare_round()
        while self.is_battle_ongoing():
            action_monomer = self.get_action_monomer()
            if not action_monomer.data.get("is_roundboundaries", False):
                self.on_monomer_action(self.get_action_monomer())
            else:
                action_monomer.reduced_action_value = 0.0
                break

    def on_monomer_action(self, monomer: Monomer):
        for i in range(len(self.monomers)):
            self.monomers[i].prepare_before_other_action()
        if monomer.prepare_before_action() != SKIP and self.is_battle_ongoing():
            monomer.start_action()
        monomer.reduced_action_value = 0.0

    def prepare_round(self):
        for i in range(len(self.monomers)):
            self.monomers[i].prepare_before_the_round()

    def get_action_monomer(self):
        self.monomers: list[Monomer | RoundBoundaries] = (
            self.active.monomers + self.passive.monomers + [self.round_boundaries]
        )
        self.monomers = sorted(self.monomers, key=lambda x: x.get_action_value())
        action_value_to_reduce = self.monomers[0].get_action_value()
        for i in range(len(self.monomers)):
            self.monomers[i].reduce_action_value(action_value_to_reduce)
        return self.monomers[0]

    def _is_battle_ongoing(self):
        return self.is_active_survive() and self.is_passive_survive()

    def is_battle_ongoing(self):
        if not (is_battle_ongoing := self._is_battle_ongoing()):
            self.create_round_logger()
            self.controller.add_logger(f"\n战斗结束：{'主动' if self.is_active_survive() else '被动'}方胜利")
        return is_battle_ongoing

    def is_active_survive(self):
        for monomer in self.active.monomers:
            if monomer.hp > 0:
                return True
        return False

    def is_passive_survive(self):
        for monomer in self.passive.monomers:
            if monomer.hp > 0:
                return True
        return False

    def prepare_fighting(self):
        for monomer in self.monomers:
            monomer.prepare_before_fighting()
