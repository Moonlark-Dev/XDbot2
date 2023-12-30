from . import _error, _lang
from .etm import data
from .sign import sign
from .userinfo import panel


from nonebot.adapters.onebot.v11 import MessageEvent
from nonebot.matcher import Matcher


import json
import traceback


@panel.handle()
@sign.handle()
async def unread_email_reminder(matcher: Matcher, event: MessageEvent):
    try:
        reminded_data = json.load(open("data/email.reminded.json", encoding="utf-8"))
        if data.emails.get(event.get_user_id()):
            email_count = 0
            for email in data.emails[event.get_user_id()]:
                if email not in (reminded_data.get(event.get_user_id()) or []):
                    email_count += 1
            if email_count != 0:
                await matcher.send(
                    _lang.text(
                        "email.remind",
                        [len(data.emails[event.get_user_id()])],
                        event.get_user_id(),
                    )
                )
                reminded_data[event.get_user_id()] = data.emails[event.get_user_id()]
                json.dump(
                    reminded_data,
                    open("data/email.reminded.json", "w", encoding="utf-8"),
                )
    except BaseException:
        await _error.report(traceback.format_exc(), matcher)
