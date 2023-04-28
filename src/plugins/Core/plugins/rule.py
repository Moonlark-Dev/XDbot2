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
    env = _globals.update(_env)
    config = rules[rule]["config"]
    for item in ast:
        if item["type"] == "call":
            if item["type"] == "*get_value":
                if item["args"][0][1:] in rules[rule]["locals"].keys():
                    return rules[rule]["locals"][item["args"][0][1:]]
                elif item["args"][0][1:] in _globals.keys():
                    return _globals[item["args"][0][1:]]


@get_driver().on_startup
async def setup_rules():
    pass
