from .etm import bag
from .send_email import submit_email
from ._utils import finish
from .etm import data, json2items, merger
from .su import su
from nonebot_plugin_apscheduler import scheduler
from nonebot import logger, on_command
from nonebot.matcher import Matcher
from nonebot.adapters.onebot.v11 import MessageEvent
from nonebot.adapters.onebot.v11 import Bot
from nonebot.adapters.onebot.v11 import Message
from nonebot.adapters.onebot.v11 import MessageSegment
from nonebot.params import CommandArg
import traceback
import time
from . import _lang
from . import _error
import json
import hashlib
from typing import List

try:
    json5 = __import__("json5")
except Exception:
    json5 = json


@scheduler.scheduled_job("cron", day="*", id="remove_emails")
async def _():
    emails = json.load(open("data/su.mails.json", encoding="utf-8"))
    items = emails.items()
    for email_id, data in items:
        if time.time() - data["time"] >= 2592000:  # 30d
            emails.pop(email_id)
            logger.info(f"已删除邮件 {email_id}")
    json.dump(
        data,
        open("data/su.mails.json", "w", encoding="utf-8"),
        ensure_ascii=False,
        indent=4,
    )

def render_email(data, user_id):
    email = _lang.text(
        "email.email",
        [
            data["subject"],
            time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(data["time"])),
            data["from"],
            data["message"],
        ],
        user_id,
    )

    if data["items"]:
        email += _lang.text("email.items", [], user_id)
        length = 0
        for item in json2items.json2items(data["items"]):
            length += 1
            email += f'\n{length}. {item.data["display_name"]} x{item.count}'
    return email


@su.handle()
async def su_mail(event: MessageEvent, message: Message = CommandArg()) -> None:
    try:
        argv = message.extract_plain_text().splitlines()[0].strip().split(" ")
        if argv[0] in ["mail", "邮箱", "email"]:
            data = json.load(open("data/su.mails.json", encoding="utf-8"))
            if argv[1] in ["create"]:
                mail_id = hashlib.sha1(str(time.time()).encode("utf-8")).hexdigest()[:7]
                rules = []
                for arg in argv:
                    if arg.startswith("--"):
                        rules.append(arg[2:].split("="))
                data[mail_id] = {
                    "message": "\n".join(str(message).split("\n")[2:]),
                    "from": "XDBOT",
                    "subject": str(message).split("\n")[1],
                    "rules": rules,
                    "items": [],
                    "time": time.time(),
                    "id": mail_id,
                }
                json.dump(
                    data,
                    open("data/su.mails.json", "w", encoding="utf-8"),
                    ensure_ascii=False,
                    indent=4,
                )
                await su.finish(f"邮件 {mail_id} 创建成功")
            elif argv[1] in ["delete"]:
                if argv[2] in data.keys():
                    data.pop(argv[2])
                    json.dump(
                        data,
                        open("data/su.mails.json", "w", encoding="utf-8"),
                        ensure_ascii=False,
                        indent=4,
                    )
                    await su.finish(f"邮件 {argv[2]} 删除成功")
            elif argv[1] in ["edit"]:
                if len(argv) <= 3:
                    await su.finish(f"可编辑内容：{' '.join(data[argv[2]].keys())}")
                elif len(str(message).splitlines()) < 2:
                    await su.finish(f"{argv[2]}::{argv[3]} -> {data[argv[2]][argv[3]]}")
                elif argv[2] in data.keys():
                    data[argv[2]][argv[3]] = json5.loads(
                        "\n".join(message.extract_plain_text().splitlines()[1:])
                    )
                    json.dump(
                        data,
                        open("data/su.mails.json", "w", encoding="utf-8"),
                        ensure_ascii=False,
                        indent=4,
                    )
                    await su.finish(f"邮件 {argv[2]} 编辑成功")
            elif argv[1] in ["view"]:
                await su.finish(render_email(data[argv[2]], event.get_user_id()))
            elif argv[1] in ["submit"]:
                await submit_email(data[argv[2]])
                await su.finish("完成！")
    except BaseException:
        await _error.report(traceback.format_exc())


@on_command("查看邮件", aliases={"view-emails", "ve", "ckyj"}).handle()
async def view_emails(matcher: Matcher, bot: Bot, event: MessageEvent):
    try:
        user_id = event.get_user_id()
        if data.emails.get(user_id):
            node_messages: List[MessageSegment] = []
            for email_id in data.emails[user_id]:
                try:
                    node_messages.append(
                        MessageSegment.node_custom(
                            user_id=event.self_id,
                            nickname=_lang.text("email.id", [email_id], user_id),
                            content=render_email(
                                json.load(open("data/su.mails.json", encoding="utf-8"))[
                                    email_id
                                ],
                                event.user_id,
                            ),
                        )
                    )
                except KeyError:
                    pass
            await bot.call_api(
                f"send_{'group' if event.get_session_id().split('_')[0]  == 'group' else 'private'}_forward_msg",  # noqa: E501
                messages=node_messages,
                user_id=int(event.get_user_id()),
                group_id=event.dict().get("group_id"),
            )
        else:
            pass  # TODO 没有可读邮件的提示
    except BaseException:
        await _error.report(traceback.format_exc(), matcher)


@on_command("领取全部", aliases={"全部领取", "claim-all", "lqqb", "qblq"}).handle()
async def claim_all(matcher: Matcher, event: MessageEvent):
    try:
        all_items = []
        emails_data = json.load(open("data/su.mails.json", encoding="utf-8"))
        user_id = event.get_user_id()
        for email_id in data.emails[user_id]:
            try:
                all_items += emails_data[email_id]["items"]
            except KeyError:
                pass
        for item in all_items:
            bag.add_item(user_id, item["id"], item["count"], item["data"])
        data.emails[user_id] = []
        item_list = ""
        length = 0

        for item in merger.merge_item_list(json2items.json2items(all_items)):
            length += 1
            item_list += f"\n{length}. {item.data['display_name']} x{item.count}"
        await finish("email.get", [item_list], event.user_id)

    except BaseException:
        await _error.report(traceback.format_exc(), matcher)


# [HELPSTART] Version: 2
# Command: view-emails
# Usage: view-emails
# Info: 邮件列表
# Command: claim-all
# Usage: claim-all
# Info: 领取邮箱物品
# [HELPEND]
