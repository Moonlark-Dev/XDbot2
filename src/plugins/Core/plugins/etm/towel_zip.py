from .item import Item
from . import achievement, bag
from .. import _lang


class TowelZip(Item):

    def on_register(self):
        self.item_id = "towel.zip"
        self.basic_data = {
            "display_name": "压缩毛巾",
            "display_message":
            "我们这个压缩毛巾体积小方便携带，拆开一包，放水里就变大，怎么扯都扯不坏，用来擦脚，擦脸，擦嘴都是很好用的，你看打开以后像圆饼一样大小，放在水里遇水变大变高，吸水性很强的。打开以后，是一条加大加厚的毛巾，你看他怎么挣都挣不坏，好不掉毛不掉絮，使用七八次都没问题，出差旅行带上它非常方便，用它擦擦脚，再擦擦嘴，擦擦脸，干净卫生。什么?在哪里买?下方小黄车，买五包送五包，还包邮。",
            "price": 9.9
        }

    def use_item(self):
        achievement.unlock("遇水变大变高", self.user_id)
        bag.add_item(self.user_id, "towel", 16, {})
        return _lang.text("towel_zip.used", [], self.user_id)


class Towel(Item):

    def on_register(self):
        self.item_id = "towel"
        self.basic_data = {
            "display_name": "毛巾",
            "display_message":
            "我们这个压缩毛巾体积小方便携带，拆开一包，放水里就变大，怎么扯都扯不坏，用来擦脚，擦脸，擦嘴都是很好用的，你看打开以后像圆饼一样大小，放在水里遇水变大变高，吸水性很强的。打开以后，是一条加大加厚的毛巾，你看他怎么挣都挣不坏，好不掉毛不掉絮，使用七八次都没问题，出差旅行带上它非常方便，用它擦擦脚，再擦擦嘴，擦擦脸，干净卫生。什么?在哪里买?下方小黄车，买五包送五包，还包邮。",
            "price": 0.62,
            "useable": False
        }
