from .monomer import Monomer


class Controller:
    def __init__(self, active: list[Monomer], passive: list[Monomer]) -> None:
        self.active = active
        self.passive = passive
        self.logs = []

    def add_logger(self, message: str):
        self.logs[-1] += message

    def create_logger_block(self, message: str = ""):
        self.logs.append([message])
