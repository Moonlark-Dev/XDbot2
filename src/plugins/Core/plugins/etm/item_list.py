from .dice import Dice
from .auto_sign_coupon import AutoSignCoupon, AutoSignCouponActived
from .talisman import Talisman
from .book_and_quill import BookAndQuill
from .pawcoin import PawCoin
from .pouch import Pouch
from .archfiend_dice import ArchfiendDice
from .mystery_box import MysteryBoxLevel1, MysteriousShard, MysteryBoxLv3
from .vimcoin import VimCoin
from .duel_things import Weapons, Ball
from .experience import Experience
from .towel_zip import TowelZip, Towel

ITEMS = {
    "dice": Dice,
    "mysterybox_lv1": MysteryBoxLevel1,
    "book_and_quill": BookAndQuill,
    "talisman": Talisman,
    "pouch": Pouch,
    "archfiend_dict": ArchfiendDice,
    "towel.zip": TowelZip,
    "towel": Towel,
    "vimcoin": VimCoin,
    "pawcoin": PawCoin,
    "exp": Experience,
    "mysterious_shard": MysteriousShard,
    "auto_sign_coupon": AutoSignCoupon,
    "auto_sign_coupon_actived": AutoSignCouponActived,
    "weapons": Weapons,
    "ball": Ball,
    "mysterybox_lv3": MysteryBoxLv3,
}
