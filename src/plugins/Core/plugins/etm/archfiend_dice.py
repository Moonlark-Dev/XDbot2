from .item import Item
from . import economy
from .user import remove_hp
import random
from .._utils import lang


class ArchfiendDice(Item):
    def on_register(self):
        self.basic_data = {
            "display_name": "恶魔骰子",
            "display_message": (
                "Straight from Kickback City！\n \n"
                "消耗 6.6vi 在 1 和 6 之间滚动，增益介于 -45HP 和 +45HP 之间。\n"
                "如果你掷出了 6，你将失去这个骰子并获得 75 vimcoins"
            ),
            "maximum_stack": 1,
            "price": 37,
        }
        self.item_id = "archfiend_dice"

    def use(self, _arg):
        if not economy.use_vimcoin(self.user_id, 6.6):
            return [lang.text("currency.no_money", [6.6], self.user_id)]
        match random.randint(1, 12):
            case 1 | 2:
                remove_hp(self.user_id, 45)
                return [lang.text("archfient_dice.info_1_5", [1, -45], self.user_id)]
            case 3 | 4:
                remove_hp(self.user_id, 30)
                return [lang.text("archfient_dice.info_1_5", [2, -30], self.user_id)]
            case 5 | 6 | 7:
                remove_hp(self.user_id, 15)
                return [lang.text("archfient_dice.info_1_5", [3, -15], self.user_id)]
            case 8 | 9:
                remove_hp(self.user_id, -15)
                return [lang.text("archfient_dice.info_1_5", [4, "+15"], self.user_id)]
            case 10 | 11:
                remove_hp(self.user_id, -30)
                return [lang.text("archfient_dice.info_1_5", [5, "+30"], self.user_id)]
            case 12:
                remove_hp(self.user_id, -45)
                economy.add_vi(self.user_id, 75)
                self.count = 0
                return [lang.text("archfient_dice.info_6", [], self.user_id)]
