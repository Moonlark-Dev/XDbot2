class Contingent:
    def __init__(self, monomers: list):
        self.monomers: list = monomers
        self.enemy: Contingent
        self.battle_skill_points = 3

    def died(self, monoer):
        self.monomers.pop(self.monomers.index(monoer))
        for i in self.monomers:
            _monomer = self.monomers[i]
            _monomer.run_tigger("enemy.killed.our")
        for i in self.enemy.monomers:
            _monomer = self.monomers[i]
            _monomer.run_tigger("out.killed.enemy")
