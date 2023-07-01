from . import parser
from . import style
# from rich import print

def md2img(markdown: str, output_path: str) -> None:
    ast = style.init_style(style.init_lists(style.init_pre(style.init_links(parser.parse(markdown)))))
    size = style.get_size(ast)
    # print(ast)
    try:
        bg_color = style.default_style["html"]["background_color"]
    except KeyError:
        bg_color = (255, 255, 255, 255)
    style.draw(ast, size, bg_color).save(output_path)
