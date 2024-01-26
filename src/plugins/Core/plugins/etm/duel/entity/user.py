from ..entity import Entity
from ...bag import get_user_bag
from ..item import DuelItem

class User(Entity):

    def __init__(self, user_id: str) -> None:
        super().__init__()
        self.user_id: str = user_id
        self.items: list[DuelItem] = [i for i in get_user_bag(self.user_id) if isinstance(i, DuelItem)]
        self.setup_items_effect()
