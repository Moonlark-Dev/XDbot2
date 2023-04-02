import json
import rich
import time

compiler_version = "v2.0.0"


def codegen(ast: list, path: str = "./helloworld") -> None:
    xrc = []
    rule_name = path.split("/")[-1]
    xri = {
        "name": rule_name,
        "namespace_id": rule_name,
        "author": None,
        "version": "v1.0.0",
    }

    rich.print("-----------------------------------")
    rich.print(ast)
    for item in ast:
        rich.print("-----------------------------------")
        rich.print(item)
        if item["call"] == "set_info":
            xri[item["name"]] = item["value"]
        else:
            xrc.append(item)
    xri["build_time"] = time.time()
    xri["compiler_version"] = compiler_version

    json.dump(xri, open(f"{path}.xri", "w", encoding="utf-8"))  # , indent=4)
    json.dump(xrc, open(f"{path}.xrc", "w", encoding="utf-8"))  # , indent=4)
