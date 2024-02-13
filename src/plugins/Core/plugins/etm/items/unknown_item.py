from types import NoneType
from ..item import Item


class UnknownItem(Item):

    def on_register(self) -> None:
        self.item_id = "unknown"
        self.setup_basic_data(
            display_name=self.text("display_name"),
            display_message=self.text("display_message")
        )