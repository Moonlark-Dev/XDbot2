from .item import Item


class PawCoin(Item):
    def on_register(self):
        self.basic_data = {
            "display_name": "猫掌币",
            "display_message": "可用于兑换使用"  # 具体的锅盖来写
        }
        self.item_id = "pawcoin"

    def use(self, args):
        pass  # TODO 使用 pawc 提示
