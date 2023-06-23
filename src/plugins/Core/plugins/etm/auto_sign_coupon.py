from .item import Item
from . import bag
from .. import _lang
from . import data as _data
from .. import sign
from .. import email
import time
from nonebot import require
from nonebot_plugin_apscheduler import scheduler
require("nonebot_plugin_apscheduler")


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


@scheduler.scheduled_job("cron", second="0", minute="55", hour="23", day="*", id="auto_sign_coupon")
async def auto_sign_coupon():
    users = _data.basic_data.keys()
    for u in users:
        ub = bag.get_user_bag(u)
        for i in ub:
            if i.item_id == "auto_sign_coupon_actived":
                await email.send_email(
                    u,
                    _lang.text("asc.signed_1", [time.strftime("%Y-%m-%d")], u),
                    _lang.text("asc.signed_2", [], u)+"\n"+sign._sign(u)
                )
                i.count -= 1
