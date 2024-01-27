from typing import Any
from ..merger import merge_item_list
from ..item import Item
import random


def json2items(items, user_id=None) -> list:
    ...


def add_item(user_id, item_id, item_count=1, item_data={}):
    ...


class CommonRubbish(Item):
    ITEM_ID_LIST = ["pouch", "towel.zip", "towel", "mysterious_shard", "book_and_quill"]

    def on_register(self):
        self.item_id = "common_rubbish"
        self.setup_basic_data(
            display_name=self.text("display_name"),
            display_message=self.text("display_message"),
            price=10,
        )

    def get_items(self) -> list[dict[str, Any]]:
        return self.data.get(
            "items",
            [
                {"id": item_id, "count": random.randint(1, 5), "data": {}}
                for item_id in random.choices(self.ITEM_ID_LIST, k=2)
            ],
        )

    def use(self, args):
        try:
            count = int(args)
        except BaseException:
            count = 1
        count = min(count, self.count)

        items = [item_list for item_list in self.get_items() for _ in range(count)]
        self.count -= count

        items = merge_item_list(json2items(items))
        message = self.text("use_title", [count])
        length = 1
        for item in items:
            add_item(self.user_id, item.item_id, item.count, item.data)
            message += self.text(
                "use_item", [length, item.data["display_name"], item.count]
            )
            length += 1
        return [message]
