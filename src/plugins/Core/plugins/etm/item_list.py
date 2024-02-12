from typing import TYPE_CHECKING, Type
from .item import Item
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
from .items.duel.passive.magic_cat import (
    MagicCatHead,
    MagicCatBall,
    MagicCatFoot,
    MagicCatBody,
    MagicCatRope,
    MagicStick,
)
from .items.duel.consumables.firecracker import Firecracker

ITEMS = {}


def register_item(item: Type[Item]) -> None:
    ITEMS[item(1, {}, None).item_id] = item


def register_items(items: list[Type[Item]]) -> None:
    for item in items:
        register_item(item)


register_items(
    [
        Dice,
        MysteryBoxLevel1,
        BookAndQuill,
        Talisman,
        Pouch,
        CommonRubbish,
        ArchfiendDice,
        TowelZip,
        MagicCatHead,
        Towel,
        VimCoin,
        PawCoin,
        GptMonthlyPass,
        Experience,
        MysteriousShard,
        AutoSignCoupon,
        AutoSignCouponActived,
        MysteryBoxLv3,
        Stick,
        MagicCatBall,
        MagicCatFoot,
        MagicCatBody,
        MagicCatRope,
        MagicStick,
        Firecracker,
    ]
)
