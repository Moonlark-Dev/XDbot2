from .dice import Dice
from .talisman import Talisman
from .book_and_quill import BookAndQuill
from .pouch import Pouch
from .vimcoin import VimCoin
from .experience import Experience
from .towel_zip import TowelZip, Towel

ITEMS = {
    "dice": Dice,
    "book_and_quill": BookAndQuill,
    "talisman": Talisman,
    "pouch": Pouch,
    "towel.zip": TowelZip,
    "towel": Towel,
    "vimcoin": VimCoin,
    "exp": Experience,
    "auto_sign_coupon": AutoSignCoupon,
    "auto_sign_coupon_actived": AutoSignCouponActived
}


def json2items(items, user_id=None):
    item_list = []
    for item in items:
        item_list.append((
            ITEMS[item["id"]](item["count"], item["data"], user_id)
        ))
    return item_list
