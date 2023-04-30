from .rulev3c import compiler
from nonebot import on_command, on_message, on_regex, get_driver

DEFAULT_RULE_CONFIG = {
    "version": "0.1.0",
    "author": "<unknown>",
    "public_namespace": 0
}
rules = {"_": {"config": DEFAULT_RULE_CONFIG, "ast": [], "locals": []}}
_globals = {}


async def _call_function(func, args=[], rule={}, _env={}):
    match func:
        case "*get_value":
            return (rules[rule].get(args[0][1:]) or
                    _env.get(args[0][1:]) or
                    _globals.get(args[0][1:]))
        case "match":
            pass
        case "command":
            pass
        case "on":
            pass
        case "send":
            await _env["_match"].send("".join(args))
        case "==":
            return args[0] == args[1]
        case "+":
            pass
        case "-":
            pass
        case "*":
            pass
        case "/":
            pass
        case "format":
            pass
        case "++":
            pass
        case "<":
            pass
        case "<=":
            pass
        case ">":
            pass
        case ">=":
            pass
        case "*get":
            pass
        case _:
            pass


async def call_function(rule, func, args, _env={}):
    for i in range(len(args)):
        args[i] = await run_rule(rule, args, _env)
    return await _call_function(func, args, rule, _env)


async def run_rule(rule, ast, _env={}):
    # config = rules[rule]["config"]
    if type(ast) != list:
        return ast
    for item in ast:
        match item["type"]:
            case "call":
                ret = await call_function(rule, await run_rule(rule, item["func"], _env), item["args"], _env)
                if ret:
                    return ret
            case "eval":
                pass
            case "var":
                rules[rule]["locals"][item["name"]] = await run_rule(rule, item["value"], _env)
            case "del":
                for var in item["name"]:
                    try:
                        rules[rule]["locals"].pop(var)
                    except KeyError:
                        try:
                            _env.pop(var)
                        except KeyError:
                            try:
                                _globals.pop(var)
                            except KeyError:
                                pass
            case _:
                pass


@get_driver().on_startup
async def setup_rules():
    pass
