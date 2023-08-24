class Contingent:
    def __init__(self, monomers: list):
        self.monomers: list = monomers
        self.enemy: Contingent
        self.battle_skill_points = 3