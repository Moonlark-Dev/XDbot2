from .item import Item
from . import economy


class VimCoin(Item):
    def on_register(self):
        self.item_id = "vimcoin"
        self.basic_data = {"display_name": "VimCoin", "display_message": "XDbot2 通用货币"}

    def _after_register(self):
        if self.user_id:
            economy.add_vi(self.user_id, self.count)
            self.count = 0
