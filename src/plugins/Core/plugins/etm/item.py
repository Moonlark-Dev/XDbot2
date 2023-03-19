from .item_basic_data import BASIC_DATA
import traceback


class Item:
    def __init__(self, count, data, user_id):
        self.count = count
        self.item_id = "dice"
        self.basic_data = {}
        # 初始化
        self.init()
        # 设置 NBT
        self.data = BASIC_DATA.copy()
        self.data.update(self.basic_data)
        self.data.update(data)
        self.user_id = user_id

    def init(self):
        pass

    def _use(self):
        pass

    def use(self, count, _):
        if self.count >= count:
            msg = []
            for _ in range(count):
                try:
                    self.count -= 1
                    msg.append(self._use())
                except BaseException:
                    msg.append(f"发生错误：{traceback.format_exc()}")
        else:
            msg = [f"错误：数量不足（拥有 {self.count} 个）"]
        return msg

    def drop(self, count):
        if self.count >= count:
            self.count -= count
            return True
        else:
            return False
        
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

    def add(self, count, _data = {}):
        data = BASIC_DATA.copy()
        data.update(self.basic_data)
        data.update(_data)
        if data == self.data:
            return self._add(count)
        
