import json
from PIL import ImageFont, Image, ImageDraw
import os.path

path: str = os.path.dirname(os.path.abspath(__file__))
default_style: dict = json.load(open(
    os.path.join(path, "default_style/style.json"), encoding="utf-8"))
nodes_needed_nl: list = ["h1", "h2", "h3", "h4", "h5", "h6", "p", "pre", "ol", "ul", "li", "blockquote"]
css_not_passed: dict = json.load(open(
    os.path.join(path, "css_not_passed.json"),
    encoding="utf-8"
))

def parse_style(item: dict | str | None) -> dict:
    if not item:
        return {}
    elif isinstance(item, str):
        return {}       # TODO 解析 CSS
    else:
        return item

def init_links(_ast: list) -> list:
    ast = _ast.copy()
    for i in range(len(ast)):
        item = ast[i]
        if isinstance(item, dict):
            if item["type"] == "a":
                item["style"] = {"color": "#0000ff"}
                item["innerHTML"].append({
                    "type":      "span",
                    "style":     {"color": "#00ff00"},
                    "innerHTML": [" (", item["href"], ")"]
                })
            else:
                item["innerHTML"] = init_links(item["innerHTML"])
    return ast

def init_lists(_ast: list) -> list:
    ast = _ast.copy()
    for i in range(len(ast)):
        item = ast[i]
        if isinstance(item, dict):
            if item["type"] == "li" and item["parentNode"] == "ol":
                item["innerHTML"].insert(0, f"{item['length']}. ")
            elif item["type"] == "li" and item["parentNode"] == "ul":
                item["innerHTML"].insert(0, "· ")
            item["innerHTML"] = init_lists(item["innerHTML"])
    return ast

def init_pre(_ast: list) -> list:
    ast = _ast.copy()
    code_data = []
    for i in range(len(ast)):
        item = ast[i]
        if isinstance(item, dict):
            if item["type"] == "code" and item["parentNode"] == "pre":
                code_data.append([i, item["class"].split("-")[1]])
            else:
                item["innerHTML"] = init_pre(item["innerHTML"])
    temp1 = 0
    for pos, lang in code_data:
        ast.insert(pos + temp1, lang)
        ast.insert(pos + temp1 + 1, {"type": "br", "innerHTML": []})
        temp1 += 2
    return ast


def init_style(_ast: list, inherited_style: dict = {}) -> list:
    ast = _ast.copy()
    nlpos = []
    inherited_style = inherited_style.copy()
    for key in list(inherited_style.keys()):
        if key in css_not_passed:
            inherited_style.pop(key)
    for i in range(len(ast)):
        item = ast[i]
        if isinstance(item, dict):
            _style = (default_style.get(item["type"]) or {}).copy()
            _style.update(inherited_style.copy())
            _style.update(parse_style(item.get("style")).copy())
            item["style"] = _style.copy()
            # 处理边距
            if item["style"].get("margin"):
                item["style"]["margin-top"] = item["style"].get("margin")
                item["style"]["margin-bottom"] = item["style"].get("margin")
                item["style"]["margin-left"] = item["style"].get("margin")
                item["style"]["margin-right"] = item["style"].get("margin")
                item["style"].pop("margin")
            if item["style"].get("padding"):
                item["style"]["padding-top"] = item["style"].get("padding")
                item["style"]["padding-bottom"] = item["style"].get("padding")
                item["style"]["padding-left"] = item["style"].get("padding")
                item["style"]["padding-right"] = item["style"].get("padding")
                item["style"].pop("padding")
            temp2 = {
                "margin-top": 0,
                "margin-bottom": 0,
                "margin-left": 0,
                "margin-right": 0,
                "padding-top": 0,
                "padding-bottom": 0,
                "padding-left": 0,
                "padding-right": 0
            }
            temp2.update(item["style"])
            temp2["margin-top"] += temp2.pop("padding-top")
            temp2["margin-bottom"] += temp2.pop("padding-bottom")
            temp2["margin-left"] += temp2.pop("padding-left")
            temp2["margin-right"] += temp2.pop("padding-right")
            for key, value in list(temp2.items()):
                if key in item["style"].keys() or value:
                    item["style"][key] = value
            
            item["innerHTML"] = init_style(item["innerHTML"], item["style"])
            if item["type"] in nodes_needed_nl:
                nlpos.append(i)
        elif isinstance(item, str):
            _style = (default_style.get("text") or {}).copy()
            _style.update(inherited_style.copy())
            # print(_style)
            ast[i] = {
                "type": "text",
                "style": _style.copy(),
                "innerHTML": [item]
            }
    temp1 = 0
    for pos in nlpos:
        ast.insert(pos + temp1 + 1, {"type": "br", "style": {}, "innerHTML": {}})
        temp1 += 1
    return ast

# TODO 计算自适应

def get_size(ast: list) -> tuple[int, int]:#, list]:
    size = [0, 0]
    line_size = [0, 0]
    for item in ast:
        match item["type"]:
            case "text":
                widget_size = list(ImageFont.truetype(
                        item["style"].get("font-family") or os.path.join(
                            path, "font/HYRunYuan-55W.ttf"),
                        item["style"].get("font-size") or\
                                default_style["text"].get("font-size") or 20)\
                        .getsize(item["innerHTML"][0]))
            case "br":
                size[0] = max(size[0], line_size[0])
                size[1] += line_size[1]
                line_size = [0, 0]
                continue
            case _:
                widget_size = list(get_size(item["innerHTML"]))
                widget_size[0] += (item["style"].get("margin-left") or 0) + (item["style"].get("margin-right") or 0)
                widget_size[1] += (item["style"].get("margin-top") or 0) + (item["style"].get("margin-bottom") or 0)
        item["size"] = widget_size
        line_size[0] += widget_size[0]
        line_size[1] = max(line_size[1], widget_size[1])
    size[0] = max(size[0], line_size[0])
    size[1] += line_size[1]
    return tuple(size)

        
def draw(ast: dict, size: tuple, background_color: tuple = (255, 255, 255, 0)) -> Image:
    img = Image.new("RGBA", size, background_color)
    dr = ImageDraw.Draw(img)
    pos = [0, 0]
    line_height = 0
    for item in ast:
        # 渲染背景
        if item["style"].get("background-color"):
            dr.rectangle((pos[0], pos[1], pos[0] + item["size"][0], pos[1] + item["size"][1]), fill=item["style"]["background-color"])
        # 渲染内容
        match item["type"]:
            case "text":
                font = ImageFont.truetype(item["style"].get(
                    "font-family") or os.path.join(
                        path, "font/HYRunYuan-55W.ttf"
                    ), item["style"].get(
                        "font-size"
                    ) or default_style["text"].get(
                        "font-size"
                    ) or 20
                )
                # 处理外边距
                pos[0] += item["style"].get("margin-left") or 0
                pos[1] += item["style"].get("margin-top") or 0
                # 绘制
                dr.text(
                    tuple(pos),
                    item["innerHTML"][0],
                    font = font,
                    fill = item["style"].get("color") or "#000",
                    stroke_width = 1 if item["style"].get("font-weight") == "bold" else 0,
                    stroke_fill = item["style"].get("color") or "#000"
                )
                pos[0] += item["size"][0]
                line_height = max(line_height, item["size"][1])
            case "br":
                pos[0] = 0
                pos[1] += line_height
                line_height = 0
            case _:
                # 处理外边距
                pos[0] += item["style"].get("margin-left") or 0
                pos[1] += item["style"].get("margin-top") or 0
                img.alpha_composite(
                    draw(item["innerHTML"], item["size"]),
                    tuple(pos)
                )
                # 处理外边距
                pos[0] -= item["style"].get("margin-left") or 0
                pos[1] -= item["style"].get("margin-top") or 0
                pos[0] += item["size"][0]
                line_height = max(line_height, item["size"][1])

    return img




    


