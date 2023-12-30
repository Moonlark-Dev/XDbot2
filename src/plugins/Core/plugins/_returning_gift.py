from . import _lang as lang
from .email import send_email


async def create_returning_gift(user_id: str) -> None:
    """
    发放回归礼物 (#498)

    Args:
        user_id (str): 用户 ID
    """
    await send_email(
        user_id,
        lang.text("sign.returning_email_subject", [], user_id),
        lang.text("sign.returning_email_message", [], user_id),
        [
            {
                "id": "vimcoin",
                "count": 500,
                "data": {}
            }
        ]
    )