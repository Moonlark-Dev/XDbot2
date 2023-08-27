class Contingent:
    def __init__(self, monomers: list):
        self.monomers: list = monomers
        self.enemy: Contingent
        self.battle_skill_points = 3
        for i in range(len(self.monomers)):
            self.monomers[i].set_contingent(self)

    def died(self, monoer):
        self.monomers.pop(self.monomers.index(monoer))
        for i in range(len(self.monomers)):
            _monomer = self.monomers[i]
            _monomer.run_tigger("enemy.killed.our")
        for i in range(len(self.enemy.monomers)):
            _monomer = self.enemy.monomers[i]
            _monomer.run_tigger("out.killed.enemy")

    def run_tigger(self, event: str):
        for i in range(len(self.monomers)):
            _monomer = self.monomers[i]
            _monomer.run_tigger(event)
