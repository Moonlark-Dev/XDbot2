from .item import Item


class PawCoin(Item):
    def on_register(self):
        self.basic_data = { # type: ignore
            "display_name": "猫爪币",
            "display_message": "中间印着一个猫爪的硬币，可用于「万能合成机」合成使用\n \n「喵，喵。喵？」",
            "useable": False
        }
        self.item_id = "pawcoin"

