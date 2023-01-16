import json
import os
import os.path
import time

from nonebot import get_driver
from nonebot.log import logger

from .config import Config

# 获取配置
try:
    os.remove("data/etm.items.json")
except Exception:
    pass
global_config = get_driver().config
config = Config.parse_obj(global_config)
try:
    disablePlugins = global_config.disabled
except BaseException:
    disablePlugins = []
try:
    disablePlugins += json.load(open("data/init.disabled.json"))
except BaseException:
    pass

# 初始化
# XDbot2 版本 1.0.0
logger.info("欢迎使用 XDbot2 （版本：1.0.0）")

# 初始化文件
logger.info("正在检查初始化 ...")
for dir in config.DIRECTORIES:
    if not os.path.isdir(dir):
        logger.warning(f"未找到目录 {dir} ，正在创建")
        os.mkdir(dir)
for file in config.FILES:
    if not os.path.isfile(file["path"]):
        logger.warning(f"未找到文件 {file['path']} ，正在创建")
        with open(file["path"], "w", encoding="utf-8") as f:
            f.write(file["text"])
logger.info("文件初始化完成！")

# 获取插件列表
path = os.path.abspath(os.path.dirname(__file__))
pluginList = os.listdir(os.path.join(path, "plugins"))
loadedPlugins = []
logger.info(f"找到 {pluginList.__len__()} 个文件或目录（于 {path} 下）")
logger.debug(pluginList)

# 导入插件（此导入方式不可调用）
for plugin in pluginList:
    if plugin.endswith(
            ".py") and plugin not in disablePlugins and not plugin.startswith("_"):
        try:
            __import__(f"src.plugins.Core.plugins.{plugin[:-3]}") 
            logger.info(f"成功加载插件{plugin}")
            loadedPlugins += [plugin]
        except Exception as e:
            logger.error(f"加载失败：插件{plugin}加载发生错误：{e}")
    else:
        logger.warning(f"未知或已禁用插件：{plugin}")
logger.info(f"已成功加载 {loadedPlugins.__len__()} 个插件")
# logger.debug(loadedPlugins)

# 写入数据文件
json.dump(
    {
        "version": config.VERSION,
        "plugins": loadedPlugins,
        "time": time.time(),
        "config": {
            "command_start": list(global_config.command_start)
        },
        "control": config.CONTROL_GROUP
    },
    open("data/init.json", "w", encoding="utf-8")
)
