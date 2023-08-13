import re
from nonebot.adapters.onebot.v11 import Message, MessageEvent
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11.bot import Bot
from nonebot.exception import FinishedException
from . import _error as error
from . import _lang as lang
from nonebot import on_command
import traceback
import httpx

pacman = on_command("archpackage", aliases={"apkg", "pacman", "Linux搜包", "spkg", "pkg"})


# [HELPSTART] Version: 2
# Command: pacman
# Usage: pacman <包名>
# Info: 在 archlinux.org/packages 上搜索
# Msg: 搜索Linux包
# [HELPEND]
async def send_request(package: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://archlinux.org/packages/?sort=&q={package}&maintainer=&flagged="
        )
        return response.read().decode("utf-8")


def get_packages_list(html: str):
    return (
        html[html.find("<tbody>") + 7 : html.find("</tbody>", html.find("<tbody>"))]
        .replace("<tr>", "")
        .replace("<td>", "")
        .replace("\n", "")
        .replace("</a>", "")
        .split("</tr>")
    )


def process_input(package_input):
    # 使用正则表达式删除非字母、数字、空格以外的所有字符
    filtered_input = re.sub(r"[^a-zA-Z0-9\s]+", "", package_input)
    return filtered_input


def parse_package_data(package: str):
    items = package.split("</td>")
    package_data = []
    for item in items:
        package_data.append(item.strip())
    try:
        return {
            "arch": package_data[0],
            "repo": package_data[1],
            "name": package_data[2][package_data[2].find(">") + 1 :],
            "ver": package_data[3],
            "info": package_data[4][package_data[4].find(">") + 1 :],
            "latest_update": package_data[5],
            "url": f"https://archlinux.org/packages/{package_data[1].lower()}/{package_data[0]}/{package_data[2][package_data[2].find('>')+1:]}",
        }
    except IndexError:
        return None


def parse_packages_data(packages: list):
    data = []
    for pkg in packages:
        pkgdata = parse_package_data(pkg)
        if pkgdata:
            data.append(pkgdata)
    return data


@pacman.handle()
async def search_package(event: MessageEvent, message: Message = CommandArg()):
    if str(message) == "":
        await pacman.finish(lang.text("pacman.need_pkg_name", [], event.user_id))
    try:
        packages = parse_packages_data(
            get_packages_list(await send_request(process_input(str(message))))
        )
        for package in packages:
            await pacman.send(
                lang.text(
                    "pacman.pkg_info",
                    [
                        package["name"],
                        package["ver"],
                        package["arch"],
                        package["info"],
                        package["latest_update"],
                        package["url"],
                    ],
                    event.user_id,
                )
            )
        await pacman.finish()
    except FinishedException:
        raise FinishedException()
    except BaseException:
        await error.report(traceback.format_exc(), pacman)
