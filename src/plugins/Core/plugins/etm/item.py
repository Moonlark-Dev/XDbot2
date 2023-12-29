from typing import Optional, Type, cast, overload
from .item_basic_data import BASIC_DATA
from abc import ABC, abstractmethod
import traceback
from .economy import IllegalQuantityException
from .nbt import NbtDict
from .._lang import text


class Item(ABC):
    def __init__(self, count, data, user_id):
        self.count = count
        self.item_id = ""  # dice"
        self.user_id = user_id
        self.basic_data = {}  # type: ignore
        # 初始化
        self.on_register()
        # 设置 NBT
        self.data = BASIC_DATA.copy()  # type: ignore
        self.data.update(self.basic_data)
        self.data.update(data)
        self._after_register()

        for key in list(self.data.keys()):
            try:
                self.data[key] = self.data[key].copy()
            except:
                pass

    @overload
    def setup_basic_data(
        self,
        display_name: Optional[str] = None,
        display_message: Optional[str] = None,
        price: Optional[int] = None,
        maximum_stack: Optional[int] = None,
        useable: Optional[bool] = None,
        can_be_sold: Optional[bool] = None,
        **params,
    ) -> None:
        ...

    def setup_basic_data(self, *args, **params) -> None:
        self.basic_data = params

    @abstractmethod
    def on_register(self):
        ...

    # @abstractmethod
    def _after_register(self):
        ...

    # @abstractmethod
    def use_item(self):
        ...

    # @abstractmethod
    async def async_use(self, arg):
        raise NotImplementedError

    def text(self, key: str, _format: list = []) -> str:
        return text(f"{self.item_id}.{key}", _format, self.user_id)

    async def on_use(self, arg):
        if not self.data["useable"]:
            return ["失败：物品无法被使用"]
        try:
            return (await self.async_use(arg)) or [
                text("currency.ok", [], self.user_id)
            ]
        except NotImplementedError:
            return (self.use(arg)) or [text("currency.ok", [], self.user_id)]

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
