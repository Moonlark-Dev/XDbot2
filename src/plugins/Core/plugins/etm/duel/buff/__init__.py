class Buff:
    def __init__(self) -> None:
        self.name: str = ""
        self.description: str = "无描述"
        self.adhesion: int = 0
        self.entity = None
    
    def on_init(self) -> None:
        pass

    def on_start(self) -> None:
        pass

    def on_action(self) -> None:
        pass
