from PIL import Image
import io
from pathlib import Path
from .const import *

base_path = Path(__file__).parent.joinpath("images")

BLOCKS = {
    NULL: Image.open(base_path.joinpath("stone_bricks.png")),
    WALL: Image.open(base_path.joinpath("bricks.png")),
    START: Image.open(base_path.joinpath("iron_block.png")),
    TERMINAL: Image.open(base_path.joinpath("diamond_block.png")),
    SPECIAL: Image.open(base_path.joinpath("piston_top.png")),
}


def generate(game_map: list[list[int]]) -> bytes:
    image = Image.new(
        "RGB", (len(game_map[0]) * 16, len(game_map) * 16), (51, 255, 255)
    )
    for row in range(len(game_map)):
        for column in range(len(game_map[row])):
            item = game_map[row][column]
            x0 = column * 16
            y0 = row * 16
            image.paste(BLOCKS[item], (x0, y0))
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()
