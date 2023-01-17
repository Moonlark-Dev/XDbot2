from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, Message
from nonebot.exception import FinishedException
from nonebot.params import CommandArg
import os
command_start="/"
def _help_init_():
    commands=[]
    plugindir=os.sep.join(__file__.split(os.sep)[0:-1])
    for fn in os.listdir(plugindir):
        if not fn.endswith(".py"):
            continue
        with open(plugindir+os.sep+fn,"r",encoding="utf-8") as f:
            fl=f.readlines()
            command = {}
            nums = []
            pluginname = fn.replace(".py","")
            for i in range(len(fl)):
                if fl[i].startswith("# [HELPSTART]") :
                    while not fl[i].startswith("# [HELPEND]"):
                        i+=1
                        l=fl[i]
                        if l.startswith("# !Usage "):
                            l=l.replace("# !Usage ","")
                            l=l.split(" ")
                            n=l[0]
                            nums.append(n)
                            command[n]={"num":n,"plugin":pluginname,"name":l[1]}
                            l.pop(0)
                            command[n]["usage"]=" ".join(l).replace("\n","")
                            continue
                        if l.startswith("# !Info "):
                            l=l.replace("# !Info ", "")
                            l=l.split(" ")
                            n=l[0]
                            l.pop(0)
                            command[n]["info"]=" ".join(l).replace("\n","").replace("\\n","\n")
                            continue
                    break
            for n in nums:
                commands.append(command[n])
    return commands
commands=_help_init_()

help = on_command("help", aliases={"帮助"})
@help.handle()
async def helpHandle(
        bot: Bot,
        message: Message = CommandArg()):
    argument = message.extract_plain_text()
    reply=""
    if argument == "":
        for i in commands:
            reply+=command_start+i["usage"]+"\n"
    else:
        for i in commands:
            if argument == i["name"]:
                reply+="命令用法："+command_start+i["usage"]+"\n"
                reply+=f"来源：插件{i['plugin']}的第{i['num']}条命令\n"
                reply+="说明："+i["info"]
    await help.finish(reply)

# [HELPSTART]
# !Usage 1 help [指令名]
# !Info 1 查询指定命令说明，若未指定指令名，则显示全部命令用法
# [HELPEND]

# ########### help的写法 ############
#
# 1. # [HELPSTART]
# `命令帮助开始 (注意空格不能丢,后面也最好别加空格,下同)
#
# 2. # !Usage num usage
# `对命令格式的说明 (可以有多个不同num的 !Usage)
# num 为在此插件中的命令编号(一个插件可以添加多条命令) 对应下文Info的信息
# usage 为命令格式 不需要写前缀 参数之间按空格分割 一般为 command <arg1> <arg2> ...
#
# 3. # !Info num information
# `对命令作用的说明 (可以有多个不同num的 !Info)
# num 为在此插件中的命令编号 对应上文Usage的信息
# information 为命令作用说明 可以使用\n换行
#
# 4. # [HELPEND]
# `命令帮助结束
#
# 警告：Usage一定要写在相同num的Info前面，一个num必须同时有Usage和Info，不然我也不知道会出什么bug

###################################