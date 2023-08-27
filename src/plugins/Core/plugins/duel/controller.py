class Controller:
    def __init__(self) -> None:
        self.logs = []

    def add_logger(self, message: str):
        self.logs[-1] += message
        print(message, end="")

    def create_logger_block(self, message: str = ""):
        self.logs.append([message])
        print(message, end="")
