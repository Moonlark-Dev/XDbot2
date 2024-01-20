from ._utils import *
from io import BytesIO
import matplotlib.pyplot as plt


def generate_image(latex_formula: str) -> MessageSegment:
    fig, ax = plt.subplots()
    ax.axis("off")
    ax.text(
        0.5,
        0.5,
        latex_formula,
        transform=ax.transAxes,
        fontsize=18,
        va="center",
        ha="center",
    )
    buffer = BytesIO()
    plt.savefig(buffer, bbox_inches="tight", pad_inches=0.1)
    return MessageSegment.image(buffer)


@create_command("latex")
async def _(bot, event: MessageEvent, message: Message) -> None:
    await finish(
        "latex.latex",
        [generate_image(f"${message.extract_plain_text()}$")],
        event.user_id,
        parse_cq_code=True,
    )
