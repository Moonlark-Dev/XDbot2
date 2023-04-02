# from . import types
import re

KEYWORDS = ["@command", "if", "else", "set", "let"]
EXPRS = ["==", "!=", ">=", "<=", ">", "<",
         "=", "\\+", "-", "\\*", "/", "\\++", "--"]
INFORMATION_KEYWORD = [
    "@NAMESPACE",
    "@NAME",
    "@AUTHOR",
    "@VERSION",
]
TYPE_KEYWORDS = ["int", "str", "json"]

types: dict = {
    "eol": ";",
    "indentation": r"\n( |\t)+",
    #    "version": r"v\d+\.\d+\.\d+",
    "op": ":",
    "parentheses_start": "\\(",
    "parentheses_end": "\\)",
    "optional_argument": f"\\[(((?!\\<).)+):({'|'.join(TYPE_KEYWORDS)})=(.)+\\]",
    "comma": ",",
    "argument": f"<(((?!\\<).)+):({'|'.join(TYPE_KEYWORDS)})>",
    "int": "0|-?[1-9][0-9]*",
    "string": r"\"((?!\").)*\"",
    "null_char": "",
    "information": "|".join(INFORMATION_KEYWORD),
    "keyword": "|".join(KEYWORDS),
    "var": f"(\\$[a-zA-z0-9]+:[^\\s(;|\\(|\\)))]+)|(\\$[^\\s(;|\\(|\\))]+)",
    "int": r"(0|[1-9]+)",
    "comment": r"/\*(.*)\*/",
    "identifier": "[a-zA-z0-9]+",
    "newline": r"\n",
    "expr": "|".join(EXPRS),
    "space": r" ",
    "unknown": "(.*)",
}


def parse(src_code: str) -> list:
    result: list = []
    token_regex = ""
    for key in list(types.keys()):
        token_regex += "(?P<%s>%s)|" % (key, types[key])
    callable_iterato = re.finditer(token_regex[:-1], src_code)

    # line = 0
    for mo in callable_iterato:
        if mo.lastgroup not in ["space", "null_char", "newline", "comment"]:
            # if mo.lastgroup == "eol":
            #    line += 1
            #    result.append([])
            # else:
            result.append((mo[0], mo.lastgroup))
    print(result)
    return result


if __name__ == "__main__":
    with open("./helloworld.xr", encoding="utf-8") as f:
        result = parse(f.read())
    for token in result:
        print(token)
