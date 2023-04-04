from .item import Item
import nonebot
from . import exp


class BookAndQuill(Item):

    def on_register(self):
        self.item_id = "book_and_quill"
        self.basic_data = {
            "display_name": "书与笔",
            "display_message": "",
            "price": 8,
            "maximum_stack": 1,
            "data": "",
            "author": None,
            "saved": False
        }

    async def async_use(self, _argv=""):
        argv = _argv.split(" ")
        if argv[0] == "--write":
            if not self.data["saved"]:
                self.data["data"] = " ".join(argv[1:])
                return ["已写入"]
            else:
                return ["错误：书本已被保存"]
        elif argv[0] == "--save":
            if not self.data["saved"]:
                self.data["author"] = self.user_id
                self.data["saved"] = True
                self.data["display_name"] = " ".join(
                    _argv.splitlines()[0].split(" ")[1:])
                self.data["display_message"] = "\n".join(
                    _argv.splitlines()[1:])
                exp.add_exp(self.user_id, 4)
                return ["保存成功！"]
            else:
                return ["错误：已经保存过了！"]
        else:
            author_nickname = (
                await (
                    list(
                        nonebot.get_bots().values()
                    )[0].get_stranger_info(
                        user_id=self.data['author']
                    )
                )
            )['nickname']
            author = f"{author_nickname} ({self.data['author']})"
            return [
                f"  {self.data['display_name']}\n作者：{author}\n—————————————\n{self.data['data']}"]
