from ..item import Item
from ..buff import add_buff
import time


class GptMonthlyPass(Item):

    def on_register(self):
        self.item_id = "gpt_monthly_pass"
        self.basic_data = {
            "display_name": self.text("display_name"),
            "display_message": self.text("display_message"),
            "maximum_stack": 8,
            "price": 1200,
        }

    def use(self, args):
        add_buff(self.user_id, "GptPlus++")
        return [
            self.text(
                "used",
                [time.strftime("%Y-%m-%d", time.localtime(time.time() + 2592000))],
            )
        ]
