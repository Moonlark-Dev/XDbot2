from .item_basic_data import BASIC_DATA
import traceback
from .economy import IllegalQuantityException
from .nbt import NbtDict
from .._lang import text


class Item:
    def __init__(self, count, data, user_id):
        self.count = count
        self.item_id = ""  # dice"
        self.basic_data: NbtDict = {}  # type: ignore
        # 初始化
        self.on_register()
        # 设置 NBT
        self.data: NbtDict = BASIC_DATA.copy()  # type: ignore
        self.data.update(self.basic_data)
        self.data.update(data)
        self.user_id = user_id
        self._after_register()

        for key in list(self.data.keys()):
            try:
                self.data[key] = self.data[key].copy()
            except:
                pass

    def on_register(self):
        ...

    def _after_register(self):
        ...

    def use_item(self):
        ...

    async def on_use(self, arg):
        if not self.data["useable"]:
            return ["失败：物品无法被使用"]
        try:
            return (await self.async_use(arg)) or [
                text("currency.ok", [], self.user_id)
            ]
        except AttributeError:
            return (await self.use(arg)) or [text("currency.ok", [], self.user_id)]

    def use(self, args):
        try:
            count = int(args)
        except BaseException:
            count = 1

        if count <= 0 or count >= 200:
            raise IllegalQuantityException(count)

        msg = []
        if self.count >= count:
            for _ in range(count):
                try:
                    msg.append(self.use_item())
                except BaseException:
                    msg.append(f"发生错误：{traceback.format_exc()}")
            self.count -= count
        else:
            msg = [f"错误：数量不足（拥有 {self.count} 个）"]
        return msg

    def drop(self, count):
        if self.count >= count and self.data["dispoable"]:
            self.count -= count
            return True
        else:
            return False

    def _used(self, count):
        self.count -= count

    def _add(self, count):
        if self.count + count <= self.data["maximum_stack"]:
            self.count += count
            return count
        elif self.count < self.data["maximum_stack"]:
            count -= self.data["maximum_stack"] - self.count
            self.add(count)
            return count
        else:
            return 0

    def add(self, count, _data={}):
        data = BASIC_DATA.copy()
        data.update(self.basic_data)
        data.update(_data)
        if data == self.data:
            return self._add(count)
        else:
            return 0
