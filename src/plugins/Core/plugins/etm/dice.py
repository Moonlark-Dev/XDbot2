from .item_basic_data import BASIC_DATA
from . import economy
import random
from .item import Item
from . import achievement
import traceback


class Dice(Item):
    def __init__(self, count, data, user_id):
        self.count = count
        self.item_id = "dice"
        self.basic_data = {
            "display_name": "二十面骰子",
            "display_message": "打开后随机获得：50vi ~ -50vi",
            "maximum_stack": 32,
            "int": None
        }
        self.init(data)

    def _use(self, user_id):
        self.count -= 1
        c = self.data["int"] or random.randint(1, 20)
        if c == 20:
            economy.add_vi(user_id, 50)
            return "你买了一个二十面骰子，掷出了 20，大成功！获得了 50vi！"
        elif 18 <= c <= 19 :
            economy.add_vi(user_id, 20)
            return f"你买了一个二十面骰子，掷出了 {c}，成功！获得了 20vi！"
        elif 15 <= c <= 17:
            economy.add_vi(user_id, 10)
            return f"你买了一个二十面骰子，掷出了 {c}，获得了 10vi！"
        elif 10 <= c <= 14:
            economy.add_vi(user_id, 5)
            return f"你买了一个二十面骰子，掷出了 {c}，拿回了自己的 5vi！"
        elif 2 <= c <= 9:
            return f"你买了一个二十面骰子，掷出了 {c}，一无所获……"
        elif c == 0:
            economy._add_vi(user_id, -50)
            achievement.increase_unlock_progress("什么欧皇", user_id)
            return f"你买了一个二十面骰子，掷出了 {c}，大失败！倾家荡产，丢失了50vi！"
        elif c == -1:
            achievement.unlck("特性！特性", user_id)
            return f"你买了一个二十面骰子，掷……掷……掷出了……………… {c} ？？？？？？？"
        else:
            # 笑死怎么可能掷出来啊（（（
            return f"你买了一个二十面骰子，掷……掷……掷出了……………… {c} ？？？？？？？"

    def use(self, count, _):
        if self.count >= count:
            msg = []
            for _ in range(count):
                try:
                    msg.append(self._use(self.user_id))
                except BaseException:
                    msg.append(f"发生错误：{traceback.format_exc()}")
        else:
            msg = [f"错误：数量不足（拥有 {self.count} 个）"]
        return msg

    def drop(self, count):
        if self.count >= count:
            self.count -= count
            return True
        else:
            return False
        
    def _add(self, count):
        if self.count + count <= self.data["maximum_stack"]:
            self.count += count
            return count
        elif self.count < self.data["maximum_stack"]:
            count -= self.data["maximum_stack"] - self.count
            self.add(count)
            return count
        else:
            return 0

    def add(self, count, _data = {}):
        data = BASIC_DATA.copy()
        data.update(self.basic_data)
        data.update(data)
        if data == self.data:
            return self._add(count)
        
