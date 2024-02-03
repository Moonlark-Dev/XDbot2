from typing import TYPE_CHECKING, Type
from .items.dice import Dice
from .items.auto_sign_coupon import AutoSignCoupon, AutoSignCouponActived
from .items.talisman import Talisman
from .items.rubbish import CommonRubbish
from .items.book_and_quill import BookAndQuill
from .items.pawcoin import PawCoin
from .items.pouch import Pouch
from .items.archfiend_dice import ArchfiendDice
from .items.mystery_box import MysteryBoxLevel1, MysteriousShard, MysteryBoxLv3
from .items.vimcoin import VimCoin
from .items.experience import Experience
from .items.gpt_monthly_pass import GptMonthlyPass
from .items.towel_zip import TowelZip, Towel
from .items.stick import Stick

ITEMS = {
    "dice": Dice,
    "mysterybox_lv1": MysteryBoxLevel1,
    "book_and_quill": BookAndQuill,
    "talisman": Talisman,
    "pouch": Pouch,
    "common_rubbish": CommonRubbish,
    "archfiend_dice": ArchfiendDice,
    "towel.zip": TowelZip,
    "towel": Towel,
    "vimcoin": VimCoin,
    "pawcoin": PawCoin,
    "gpt_monthly_pass": GptMonthlyPass,
    "exp": Experience,
    "mysterious_shard": MysteriousShard,
    "auto_sign_coupon": AutoSignCoupon,
    "auto_sign_coupon_actived": AutoSignCouponActived,
    "mysterybox_lv3": MysteryBoxLv3,
    "stick": Stick,
}

