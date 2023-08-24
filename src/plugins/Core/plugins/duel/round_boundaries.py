from .monomer import get_base_properties

class RoundBoundaries:

    def __init__(self) -> None:
        base_properties = get_base_properties()
        self.data = base_properties.copy()
        self.data["speed"] = 90     # 回合边界速度
        self.data["is_roundboundaries"] = True
        self.reduced_action_value: float = 0.0

    def get_action_value(self):
        return 10000 / self.data["speed"] - self.reduced_action_value
    
    def reduce_action_value(self, count: int):
        self.reduced_action_value += count

    def prepare_before_action(self) -> None:
        pass

    def prepare_before_the_round(self) -> None:
        pass