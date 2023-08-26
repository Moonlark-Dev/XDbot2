from .dice import Dice
from .auto_sign_coupon import AutoSignCoupon, AutoSignCouponActived
from .talisman import Talisman
from .book_and_quill import BookAndQuill
from .pawcoin import PawCoin
from .pouch import Pouch
from .mystery_box import MysteryBoxLevel1, MysteriousShard
from .vimcoin import VimCoin
from .weapons import Weapons
from .experience import Experience
from .towel_zip import TowelZip, Towel

ITEMS = {
    "dice": Dice,
    "mysterybox_lv1": MysteryBoxLevel1,
    "book_and_quill": BookAndQuill,
    "talisman": Talisman,
    "pouch": Pouch,
    "towel.zip": TowelZip,
    "towel": Towel,
    "vimcoin": VimCoin,
    "pawcoin": PawCoin,
    "exp": Experience,
    "mysterious_shard": MysteriousShard,
    "auto_sign_coupon": AutoSignCoupon,
    "auto_sign_coupon_actived": AutoSignCouponActived,
    "weapons": Weapons
}
