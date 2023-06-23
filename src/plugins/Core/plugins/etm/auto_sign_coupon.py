from .item import Item
from . import achievement, bag
from .. import _lang


class AutoSignCoupon(Item):
    def on_register(self):
        self.item_id = "auto_sign_coupon"
        self.basic_data = {
            "display_name": "自动签到券（未激活）",
            "display_message": "使用一次激活后可自动签到",
            "maximum_stack": 64,
        }

    def use_item(self):
        bag.add_item(self.user_id, "auto_sign_coupon_actived", 1, {})
        return _lang.text("asc.actived", [], self.user_id)
        
class AutoSignCouponActived(Item):
    def on_register(self):
        self.item_id = "auto_sign_coupon_actived"
        self.basic_data = {
            "display_name": "自动签到券（激活）",
            "display_message": "可自动签到，再次使用取消激活",
            "maximum_stack": 64,
        }

    def use_item(self):
        bag.add_item(self.user_id, "auto_sign_coupon", 1, {})
        return _lang.text("asc.inactived", [], self.user_id)