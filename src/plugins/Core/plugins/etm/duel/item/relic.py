from typing import Literal, Optional
from .passive import DuelPassiveItem


class DuelRelic(DuelPassiveItem):
    RELIC_TYPE: Literal["head", "body", "foot", "hand", "rope", "ball"]
    RELIC_SET_NAME: Optional[str]

    def __init__(self, count, data, user_id):
        super().__init__(count, data, user_id)
        self.RELIC_SET_NAME = None
