from ._utils import Json
import importlib
from nonebot.log import logger
import os
import os.path
import traceback

# 说明：
# ITCraftDevelopmentTeam/Maple-Bot 插件兼容层
# 允许在 XDbot2 加载部分 Maple-Bot 插件
# TODO 完善 Maple 兼容层

# 加载 Maple 插件
path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "maple")
plugin_list = os.listdir(path)
logger.info(f"找到 {len(plugin_list)} 个 Maple 移植插件：{plugin_list}")
plugins = {}

for plugin in plugin_list:
    if os.path.isfile(os.path.join(path, plugin))\
            and not plugin.startswith("_"):
        try:
            plugins[plugin] = {
                "module": importlib.import_module(f"src.plugins.Core.plugins.maple.{plugin[:-3]}")
            }
            logger.success(f"成功加载插件：{plugin} (maple)")
        except:
            logger.error(f"加载插件 {plugin} (maple) 失败：{traceback.format_exc()}")
            Json("_error.count.json")["count"] += 1
logger.info("Maple 兼容插件加载完成！")


def check_wam():
    return "who_at_me.py" in plugins.keys()

# [HELPSTART] Version: 2
# Command: who-at-me
# Info: 谁艾特我
# Usage: who-at-me
# Check: check_wam
# [HELPEND]
