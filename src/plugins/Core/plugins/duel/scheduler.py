from .contingent import Contingent
from .round_boundaries import RoundBoundaries
from .monomer import Monomer, SKIP


class Scheduler:
    def __init__(self, active: Contingent, passive: Contingent):
        self.active = active
        self.passive = passive
        self.round_boundaries = RoundBoundaries()
        self.monomers: list[Monomer] = (
            self.active.monomers + self.passive.monomers + [self.round_boundaries]
        )

    def start_fighting(self):
        self.prepare_fighting()
        while self.is_battle_ongoing():
            self.start_round()

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
        if monomer.prepare_before_action() != SKIP and self.is_battle_ongoing():
            monomer.start_action()
        monomer.reduced_action_value = 0.0

    def prepare_round(self):
        for i in range(len(self.monomers)):
            self.monomers[i].prepare_before_the_round()

    def get_action_monomer(self):
        self.monomers: list[Monomer] = (
            self.active.monomers + self.passive.monomers + [self.round_boundaries]
        )
        self.monomers = sorted(self.monomers, key=lambda x: x.get_action_value())
        action_value_to_reduce = self.monomers[0].get_action_value()
        for i in range(len(self.monomers)):
            self.monomers[i].reduce_action_value(action_value_to_reduce)
        return self.monomers[0]

    def is_battle_ongoing(self):
        return self.is_active_survive() and self.is_passive_survive()

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
