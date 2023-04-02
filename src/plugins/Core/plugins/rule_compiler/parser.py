from . import lexer
import json
import rich

INFORMATION_KEYWORDS = {
    "@NAME": "name",
    "@NAMESPACE": "namespace_id",
    "@AUTHOR": "author",
    "@VERSION": "version",
}

"""
def parse(tokens: list) -> list | None:
    print(tokens)
    ast = []
    while len(tokens) > 0:
        line = []
        while True:
            token = tokens.pop(0)
            if token[1] != "eol":
                line.append(token)
            else:
                break
        ast.append(parse_line(line))
    return ast
"""
EXPR_CALLS = {
    "+": "add",
    "-": "???",
    "*": "???",
    "/": "???",
    "++": "add_one",
    "==": "is",
}


class Parser:
    TOKEN_VALUE = 0
    TOKEN_TYPE = 1
    BASE_TYPES = ["string", "int"]
    EOL = "eol"
    ROOT_IDENTATION = ""
    OP = "op"
    NULL_LINE = []
    INDENTATION = "indentation"
    IGNORE_TOKEN_TYPES = ["common"]

    def __init__(self, tokens: list) -> None:
        self.tokens = tokens
        self.ast = []
        self.length = 0

    def add_ast_item(self, item: dict) -> None:
        self.ast.append(item)

    def parse(self) -> list:
        # 解析块
        self.lines = self.to_line()
        self.token_blocks = self.to_block()
        rich.print(self.token_blocks)

        # 逐块解析
        self.ast = self.parse_block(self.token_blocks)

        return self.ast

    def parse_block(self, blocks: list) -> list:
        ast = [{}]
        while len(blocks) > 0:
            print(blocks)
            block = blocks.pop(0)
            if type(block[0]) == list:
                ast[-1]["run"] = self.parse_block(block)
                ast.append({})
            else:
                while len(block) > 0:
                    token = block.pop(0)
                    if token[self.TOKEN_TYPE] == "information":
                        ast[-1]["call"] = "set_info"
                        ast[-1]["name"] = INFORMATION_KEYWORDS[token[self.TOKEN_VALUE]]
                        ast[-1]["value"] = self.parse_information_token(block)
                    elif token[self.TOKEN_TYPE] == self.EOL:
                        ast.append({})
                    elif token[self.TOKEN_TYPE] == "keyword":
                        if token[self.TOKEN_VALUE] == "@command":
                            ast[-1]["call"] = "new_command"
                            ast[-1]["name"] = block.pop(0)[self.TOKEN_VALUE]
                            ast[-1]["arguments"] = self.parse_command_arguments(block)
                        elif token[self.TOKEN_VALUE] == "if":
                            ast[-1]["call"] = "if"
                            ast[-1]["else"] = []
                            ast[-1]["condition"] = self.parse_condition(block)
                        elif token[self.TOKEN_VALUE] == "else":
                            # block.pop(0)
                            ast.pop(-1)
                            ast[-1]["else"] = self.parse_block(blocks.pop(0))
                            ast.append({})
                        elif token[self.TOKEN_VALUE] in ["set", "let"]:
                            ast[-1]["call"] = "set"
                            ast[-1]["name"] = block.pop(0)[self.TOKEN_VALUE]
                            block.pop(0)
                            print(block)
                            if self.is_expr(block):
                                print("114514", block)
                                ast[-1]["value"] = self.parse_expr_block(block)

                            else:
                                ast[-1]["value"] = self.parse_block([block])
                            ast.append({})

                    elif token[self.TOKEN_TYPE] == "identifier":
                        print("b1", block)
                        ast[-1]["call"] = "invoke"
                        ast[-1]["function"] = token[self.TOKEN_VALUE]
                        ast[-1]["arguments"] = self.parse_information_token(block)
                    elif token[self.TOKEN_TYPE] == "var":
                        print("b2", block)
                        ast[-1]["call"] = "get_var"
                        ast[-1]["name"] = token[self.TOKEN_VALUE][1:]
                        ast.append({})
                    else:
                        rich.print(f"[red]{token}")
            rich.print(ast)

        if ast[-1] == {}:
            ast.pop(-1)
        return ast

    def is_expr(self, tokens: list) -> bool:
        for token in tokens:
            if token[self.TOKEN_TYPE] == "expr":
                return True
        return False

    def parse_condition(self, tokens: list) -> list:
        condition = []
        while len(tokens) > 0:
            token = tokens.pop(0)
            if token[self.TOKEN_TYPE] != self.OP:
                condition.append(token)
        condition = self.parse_expr_block(condition)
        return condition

    def parse_expr_block(self, tokens: list, echo: int = 0) -> list:
        block = [{"b": "non-None"}]
        tokens = self.parse_parenthese(tokens)
        print(echo, f"tokens {tokens}")  # , tokens)
        while len(tokens) > 0:
            token = tokens.pop(0)
            print("tk", echo, token)
            if type(token) == list:
                if block[-1]["b"] in [None, []]:
                    block[-1]["b"] = self.parse_expr_block(token, echo=echo + 1)
                    rich.print(f"{echo}: block1 {block}")
                else:
                    block.append(
                        {
                            "call": None,
                            "a": self.parse_expr_block(token, echo=echo + 1),
                            "b": None,
                        }
                    )
                    rich.print(f"{echo}: block2 {block}")
            elif token[self.TOKEN_TYPE] == "expr":
                block[-1]["call"] = EXPR_CALLS[token[self.TOKEN_VALUE]]
            elif token[self.TOKEN_TYPE] == "eol":
                rich.print("[yellow]eol")
                return block[1:]
            else:
                if block[-1]["b"] in [None, []]:
                    block[-1]["b"] = self.parse_expr_item_token(token)
                else:
                    block.append(
                        {
                            "call": None,
                            "a": self.parse_expr_item_token(token),
                            "b": None,
                        }
                    )
            rich.print(f"{echo}: {block}")
        rich.print(f"[blue]{echo}: finish ({block[1:]})")
        return block[1:]

    def parse_expr_item_token(self, token: tuple) -> any:

        if token[self.TOKEN_TYPE] in self.BASE_TYPES:
            return json.loads(token[self.TOKEN_VALUE])
        else:
            print([token])
            return self.parse_block([[token]])

    def parse_command_arguments(self, tokens: list) -> list:
        arguments = []
        for token in tokens:
            if token[self.TOKEN_TYPE] == self.OP:
                return arguments
            elif token[self.TOKEN_TYPE] == "argument":
                argv = token[self.TOKEN_VALUE][1:-1].split(":")
                arguments.append(
                    {
                        "name": argv[0],
                        "optional": False,
                        "default": None,
                        "type": argv[1],
                    }
                )
            elif token[self.TOKEN_TYPE] == "optional_argument":
                argv = token[self.TOKEN_VALUE][1:-1].split(":")
                # print("json", argv[1].split("=")[0])
                arguments.append(
                    {
                        "name": argv[0],
                        "optional": True,
                        "default": json.loads(argv[1].split("=")[1]),
                        "type": argv[1].split("=")[0],
                    }
                )
        return arguments

    """
    def parse_expr(self, tokens: list) -> list:
        block = []
        while len(tokens) > 0:
            token = tokens.pop(0)
            if type(token) == list:
                block.append(self.parse_expr(tokens))
            else:
                ...
    """

    def parse_information_token(self, tokens: list) -> list | None:
        value = [None]
        while len(tokens) > 0:
            token = tokens.pop(0)
            if token[self.TOKEN_TYPE] == "comma":
                value.append(None)
            elif token[self.TOKEN_TYPE] != self.EOL:
                print("token", token[self.TOKEN_VALUE])
                print("value[-1]", value[-1])
                if value[-1] is None:
                    try:
                        value[-1] = json.loads(token[self.TOKEN_VALUE])
                        print(1)
                    except BaseException:
                        print(2)
                        value[-1] = self.parse_block([[token]])
                else:
                    value[-1] += json.loads(token[self.TOKEN_VALUE])
                print("value", value)
            else:
                tokens.insert(0, (";", "eol"))
                break
        if len(value) > 1:
            return value
        else:
            return value[0]

    def to_line(self) -> list:
        lines = [[]]
        for token in self.tokens:
            if token[self.TOKEN_TYPE] not in self.IGNORE_TOKEN_TYPES:
                lines[-1].append(token)
                if token[self.TOKEN_TYPE] in [self.EOL, self.OP]:
                    lines.append([])
        return lines

    def parse_parenthese(self, tokens: list) -> list:
        block = []
        while len(tokens) > 0:
            token = tokens.pop(0)
            if token[self.TOKEN_TYPE] == "parentheses_start":
                block.append(self.parse_parenthese(tokens))
            elif token[self.TOKEN_TYPE] == "parentheses_end":
                break
            else:
                block.append(token)
        return block

    def to_block(self, indentation: str = "") -> list:
        blocks = []
        # length = 0
        while len(self.lines) > 0:
            line = self.lines.pop(0)
            print(line)
            if line == self.NULL_LINE:
                continue
            token = line[0]
            if token[self.TOKEN_TYPE] == self.INDENTATION:
                if token[self.TOKEN_VALUE] == indentation:
                    length = 0
                    for token in line.copy():
                        if token[self.TOKEN_TYPE] == self.INDENTATION:
                            line.pop(length)
                        else:
                            length += 1
                    blocks.append(line)
                else:
                    if len(indentation) > len(token[self.TOKEN_VALUE]):
                        self.lines.insert(0, line)
                        return blocks
                    else:
                        # print("len", line[length:])
                        self.lines.insert(0, line)
                        blocks.append(self.to_block(token[self.TOKEN_VALUE]))
            else:
                if indentation == self.ROOT_IDENTATION:
                    blocks.append(line)
                else:
                    self.lines.insert(0, line)
                    return blocks
        return blocks


if __name__ == "__main__":
    with open("./helloworld.xr", encoding="utf-8") as f:
        parser = Parser(lexer.parse(f.read()))

    #    import rich
    rich.print(parser.parse())
