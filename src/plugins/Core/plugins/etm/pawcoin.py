from .item import Item


class PawCoin(Item):
    def on_register(self):
        self.basic_data = { # type: ignore
            "display_name": "猫爪币",
            "display_message": "可用于兑换使用（没写完）",
            "useable": False
        }
        self.item_id = "pawcoin"

