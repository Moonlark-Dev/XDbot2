import importlib
from nonebot.log import logger
import os
import os.path
import traceback

# 说明：
# ITCraftDevelopmentTeam/Maple-Bot 插件兼容层
# 允许在 XDbot2 加载部分 Maple-Bot 插件

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
logger.info("Maple 兼容插件加载完成！")