from .rulev3c import compiler
from nonebot import on_command, on_message, on_regex, get_driver

DEFAULT_RULE_CONFIG = {
    "version": "0.1.0",
    "author": "<unknown>",
    "public_namespace": 0
}
rules = {"_": {"config": DEFAULT_RULE_CONFIG, "ast": [], "locals": []}}
_globals = {}

async def run_rule(rule, ast, _env = {}):
    # config = rules[rule]["config"]
    if type(ast) != list:
        return ast
    for item in ast:
        if item["type"] == "call":
            if item["func"] == "*get_value":
                if item["args"][0][1:] in rules[rule]["locals"].keys():
                    return rules[rule]["locals"][item["args"][0][1:]]
                elif item["args"][0][1:] in _env.keys():
                    return _env[item["args"][0][1:]]
                elif item["args"][0][1:] in _globals.keys():
                    return _globals[item["args"][0][1:]]
                else:
                    return None
            elif item["func"] == "match":
                pass
            elif item["func"] == "command":
                pass
            elif item["func"] == "on":
                pass
            elif item["func"] == "send":
                await _env["_match"].send(run_rule(rule, ast, _env))
            elif item["func"] == "==":
                return run_rule(rule, item["args"][0]) == run_rule(rule, item["args"][1])
            elif item["func"] == "+":
                pass
            else:
                pass
        elif item["type"] == "var":
            rules[rule]["locals"][item["name"]] = await run_rule(rule, item["value"], _env)
        elif item["type"] == "del":
            for var in item["name"]:
                try: rules[rule]["locals"].pop(var)
                except KeyError: 
                    try: _env.pop(var)
                    except KeyError: _globals.pop(var)
                



@get_driver().on_startup
async def setup_rules():
    pass
