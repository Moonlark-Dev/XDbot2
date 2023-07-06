from . import economy
import random
from .item import Item
from .. import _lang
from . import achievement, buff
from .economy import IllegalQuantityException


class Dice(Item):
    def on_register(self):
        self.item_id = "dice"
        self.basic_data = {
            "display_name": "二十面骰子",
            "display_message": "打开后随机获得：50vi ~ -50vi",
            "maximum_stack": 32,
            "int": None
        }
        

    def result(self, c, is_data=False):
        if is_data:
            return c
        if 193 <= c <= 200:  # 20
            return 20
        elif 183 <= c <= 192:  # 18-19
            return random.randint(18, 19)
        elif 153 <= c <= 182:  # 15-17
            return random.randint(15, 17)
        elif 106 <= c <= 152:  # 10-14
            return random.randint(10, 14)
        elif 16 <= c <= 105:  # 2-9
            return random.randint(2, 9)
        elif c <= 15:  # 1
            return 1

    def use(self, args):
        if not self.data["useable"]:
            return [_lang.text("item.not_useable", [], str(self.user_id))]
        try:
            count = int(args)
        except BaseException:
            count = 1
        if count <= 0 or count > self.count:
            raise IllegalQuantityException(count)
        if count == 1:
            return [self.use_item()[0]]
        else:
            total_vim = 0
            big_success_count = 0
            big_lose_count = 0
            for _ in range(count):
                res = self.use_item()
                total_vim += res[2]
                if res[1] == 20:
                    big_success_count += 1
                elif res[1] == 1:
                    big_lose_count += 1
            return [_lang.text("dice.somedice", [
                count, total_vim, 
                big_success_count, round(big_success_count / count, 1),
                big_lose_count, round(big_lose_count / count , 1)
            ], str(self.user_id))]




    def use_item(self):
        user_id = self.user_id
        if self.data["int"] is not None:
            c = self.data["int"]
        else:
            c = random.randint(1, 200)
        c = self.result(c, self.data["int"] is not None)
        self.count -= 1
        if c == 20:  # 20
            economy.add_vi(user_id, 50)
            return _lang.text("dice.20", [c], self.user_id), c, 50
        elif 18 <= c <= 19:  # 18-19
            economy.add_vi(user_id, 20)
            return _lang.text("dice.18..19", [c], self.user_id), c, 20
        elif 15 <= c <= 17:  # 15-17
            economy.add_vi(user_id, 10)
            return _lang.text("dice.15..17", [c], self.user_id), c, 10
        elif 10 <= c <= 14:  # 10-14
            economy.add_vi(user_id, 5)
            return _lang.text("dice.10..14", [c], self.user_id), c, 5
        elif 2 <= c <= 9:  # 2-9
            return _lang.text("dice.2..9", [c], self.user_id), c, 0
        elif c == 1:  # 1
            achievement.increase_unlock_progress("什么欧皇", user_id)
            if buff.can_effect(user_id, "护符") and random.random() <= 0.75:
                buff.effect_buff(user_id, "护符")
                return _lang.text("dice.1-1", [c], self.user_id), c, 0
            else:
                economy._add_vi(user_id, -50)
                return _lang.text("dice.1-2", [c], self.user_id), c, -50
        elif c == -1:
            achievement.unlock("特性！特性", user_id)
            return _lang.text("dice.else", [c], self.user_id), c, 0
        else:
            # 笑死怎么可能掷出来啊（（（
            return _lang.text("dice.else", [c], self.user_id), c, 0
