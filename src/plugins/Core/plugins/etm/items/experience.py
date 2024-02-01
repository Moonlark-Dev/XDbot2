from ..item import Item
from .. import exp


class Experience(Item):
    def on_register(self):
        self.item_id = "exp"
        self.basic_data = {"display_name": "Experience", "display_message": "经验", "maximum_stack": 1145141919810}


    def _after_register(self):
        if self.user_id:
            exp.add_exp(self.user_id, self.count)
            self.count = 0
