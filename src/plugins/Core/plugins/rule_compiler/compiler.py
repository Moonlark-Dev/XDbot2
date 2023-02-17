from . import lexer
import sys
from . import parser
from . import visitor


def build(path: str, to_path: str = "./") -> None:
    with open(f"{path}.xr", "r", encoding="utf-8") as f:
        file = f.read()
    p = parser.Parser(lexer.parse(file))
    visitor.codegen(p.parse(), f"{to_path}{path}")


if __name__ == "__main__":
    build(sys.argv[1])
