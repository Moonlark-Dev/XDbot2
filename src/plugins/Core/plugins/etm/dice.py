from . import economy
import random
from .item import Item
from . import achievement


class Dice(Item):
    def on_register(self):
        self.item_id = "dice"
        self.basic_data = {
            "display_name": "二十面骰子",
            "display_message": "打开后随机获得：50vi ~ -50vi",
            "maximum_stack": 32,
            "int": None
        }

    def use_item(self):
        user_id = self.user_id
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
        elif c == 1:
            economy._add_vi(user_id, -50)
            achievement.increase_unlock_progress("什么欧皇", user_id)
            return f"你买了一个二十面骰子，掷出了 {c}，大失败！倾家荡产，丢失了50vi！"
        elif c == -1:
            achievement.unlck("特性！特性", user_id)
            return f"你买了一个二十面骰子，掷……掷……掷出了……………… {c} ？？？？？？？"
        else:
            # 笑死怎么可能掷出来啊（（（
            return f"你买了一个二十面骰子，掷……掷……掷出了……………… {c} ？？？？？？？"

 

    
        
