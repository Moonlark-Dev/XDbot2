from ..item import DuelItem


class DuelConsumables(DuelItem):
    def __init__(self, count, data, user_id):
        super().__init__(count, data, user_id)
        self.DUEL_ITEM_TYPE = "consumables"

    def used(self) -> None:
        self.count -= 1
        if self.count <= 0:
            self.entity.items["other"].remove(self)
