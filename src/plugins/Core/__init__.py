import json
import os
import os.path
import time
from . import get_version
import sys
import re

from nonebot import get_driver, require
from nonebot.log import logger

from .config import Config

from . import getHelp
import traceback

require("nonebot_plugin_apscheduler")

# 清理（Issue #66）
logger.info("正在清理数据")
files = os.listdir("./data")
file_list = [
    r"etm\.items\.json",
    r"preview(.*).png",
    r"setu\.(.*)\.(jpg|png)",
    r"(.*)\.ro\.(.*)"
]
try:
    for file in files:
        if re.match("|".join(file_list), file):
            os.remove(os.path.join("./data", file))
            logger.info(f"已清理 {file}")
except Exception:
    logger.error(f"清理失败：{traceback.format_exc()}")
try:
    os.remove("duel2/lock.json")
except Exception:
    pass

# 获取配置
global_config = get_driver().config
config = Config.parse_obj(global_config)
try:
    disablePlugins = global_config.disabled
except BaseException:
    disablePlugins = []
try:
    disablePlugins += json.load(open("data/init.disabled.json", encoding="utf-8"))
except BaseException:
    pass
try:
    is_develop = global_config.node_id == "develop"
except:
    is_develop = False

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
helpData = {}
pluginsModule = dict()


def check_plugin(plugin: str) -> bool:
    try:
        with open(os.path.join(path, "plugins", plugin), encoding="utf-8") as f:
            if (text := f.read()).startswith("# [DEVELOP]") and not is_develop:
                return False
            elif text.startswith("# [MASTER]") and is_develop:
                return False
    except:
        return False
    return (
        plugin.endswith(".py")
        and plugin not in disablePlugins
        and not plugin.startswith("_")
    )


# 导入插件（此导入方式不可调用）
sys.path.append(path)
for plugin in pluginList:
    if check_plugin(plugin):
        try:
            pluginsModule[plugin] = getattr(
                __import__(f"plugins.{plugin[:-3]}"), plugin[:-3]
            )
            logger.info(f"成功加载插件{plugin}")
            loadedPlugins += [plugin]
            # 读取帮助
            helpData.update(getHelp.get_plugin_help(plugin[:-3], pluginsModule[plugin]))

        except AttributeError:
            logger.warning(f"在{plugin}中找不到指令文档")
            # print(traceback.format_exc())
        except Exception as e:
            logger.error(f"加载失败：插件{plugin}加载发生错误：{e}")
            print(traceback.format_exc())

            data = json.load(open("data/_error.count.json", encoding="utf-8"))
            data["count"] += 1
            json.dump(data, open("data/_error.count.json", "w", encoding="utf-8"))
    else:
        logger.warning(f"未知或已禁用插件：{plugin}")
logger.info(
    f"已成功加载 {loadedPlugins.__len__()} 个插件，{len(helpData.keys())}个指令帮助"
)
# logger.debug(loadedPlugins)

# 写入加载数据文件
json.dump(
    {
        "version": get_version.get_version(is_develop),
        "plugins": loadedPlugins,
        "time": time.time(),
        "config": {"command_start": list(global_config.command_start)},
        "control": config.CONTROL_GROUP,
    },
    open("data/init.json", "w", encoding="utf-8"),
)

# 写入帮助文件
logger.debug(helpData)
json.dump(helpData, open("data/help.json", "w", encoding="utf-8"))
