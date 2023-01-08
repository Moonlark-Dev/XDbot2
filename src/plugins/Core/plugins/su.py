from nonebot.adapters.onebot.v11 import MessageEvent, Message
from nonebot.adapters.onebot.v11.bot import Bot
from nonebot import on_command
from nonebot.exception import FinishedException, IgnoredException
from nonebot.params import CommandArg
import traceback
import os
import time
import json
from nonebot.message import event_preprocessor 
from nonebot.permission import SUPERUSER

su = on_command("su", aliases={"超管", "superuser"}, permission = SUPERUSER)
ctrlGroup = json.load(open("data/ctrl.json", encoding="utf-8"))["control"]
blackListData = json.load(open("data/su.blackList.json"))


def reloadBlackList():
    global blackListData
    blackListData = json.load(open("data/su.blackList.json"))


@su.handle()
async def suHandle(
        bot: Bot,
        message: Message = CommandArg()):
    try:
        argument = message.extract_plain_text().split(" ")
        if argument[0] == "ban" or argument[0] == "封禁":
            data = json.load(open("data/su.blackList.json"))
            if argument[1] not in data:
                data += [argument[1]]
                await su.send(f"已封禁{argument[1]}")
            json.dump(data, open("data/su.blackList.json", "w"))
            reloadBlackList()
        elif argument[0] == "pardon" or argument[0] == "解封":
            data = json.load(open("data/su.blackList.json"))
            length = 0
            for user in data:
                if user == argument[1]:
                    data.pop(length)
                    await su.send(f"已解封{argument[1]}")
                    break
                else:
                    length += 1
            json.dump(data, open("data/su.blackList.json", "w"))
            reloadBlackList()
        elif argument[0] == "call" or argument[0] == "调用":
            await su.send(
                await bot.call_api(
                    api=argument[1],
                    data=json.loads(argument[2])))
        elif argument[0] == "ct" or argument[0] == "发言排名":
            if argument[1] == "clear" or argument[1] == "清除数据":
                fileList = os.listdir("data")
                for file in fileList:
                    if file.startswith("ct."):
                        json.dump(dict(), open(f"data/{file}", "w"))
                        await su.send(f"已重置：{file}")
        elif argument[0] == "echo" or argument[0] == "调试输出":
            await su.send(
                Message(
                    message.extract_plain_text()[argument[0].__len__() + 1:]
                )
            )
        elif argument[0] == "notice" or argument[0] == "超级广播" or argument[0] == "广播":
            text = message.extract_plain_text()[argument[0].__len__() + 1:]
            groupList = await bot.get_group_list()
            # 开始广播
            for group in groupList:
                await bot.send_group_msg(
                    message=Message(f"【超级广播】\n{text}"),
                    group_id=group['group_id']
                )
        elif argument[0] == "config" or argument[0] == "配置":
            if argument[1] == "get" or argument[1] == "获取":
                await su.send(str(json.load(open(
                    f"data/{argument[2]}.json",
                    encoding="utf-8"
                ))[argument[3]]))
            elif argument[1] == "set" or argument == "设置":
                config = json.load(open(
                    f"data/{argument[2]}.json",
                    encoding="utf-8"))
                config[argument[3]] = json.loads(
                    message.extract_plain_text()[
                        len(argument[0] + argument[1] + argument[2] + argument[3]) + 4:]
                )
                json.dump(config, open(
                    f"data/{argument[2]}.json",
                    mode="w",
                    encoding="utf-8"
                ))
        elif argument[0] == "plugins" or argument[0] == "插件管理":
            config = json.load(open("data/init.disabled.json", encoding="utf-8"))
            if argument[1] == "disable" or argument[1] == "禁用":
                if argument[2] not in config:
                    config += [argument[2]]
            elif argument[1] == "enable" or argument[1] == "启用":
                length = 0
                for conf in config:
                    if conf == argument[2]:
                        config.pop(length)
                        break
            json.dump(config, open("data/init.disabled.json", "w", encoding="utf-8"))
        elif argument[0] == "restart" or argument[0] == "重新启动":
            with open("data/reboot.py", "w") as f:
                f.write(str(time.time()))
        # 反馈
        await su.finish("完成")

    except FinishedException:
        raise FinishedException()
    except Exception:
        await bot.send_group_msg(
            message=traceback.format_exc(),
            group_id=ctrlGroup)
        await su.finish("处理失败")

@event_preprocessor
async def blackListHandle(
        bot: Bot,
        event: MessageEvent):
    try:
        if event.get_user_id() in blackListData:
            raise IgnoredException("Banned")

    except IgnoredException as e:
        raise IgnoredException(e)
    except Exception:
        await bot.send_group_msg(
            message=traceback.format_exc(),
            group_id=ctrlGroup)
 
