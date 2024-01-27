from ..item import DuelItem


class DuelPassiveItem(DuelItem):
    def __init__(self, count, data, user_id):
        super().__init__(count, data, user_id)
        self.DUEL_ITEM_TYPE = "passive"

    def on_attack(self, harm: float) -> float:
        return harm
