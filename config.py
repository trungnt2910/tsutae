from typing import Self

class Config:
    def __init__(self: Self, token: str = "", channels: dict[str, str] = {}, history_age: int = 48, history_limit: int = 20):
        self.token: str = token
        self.channels: dict[str, str] = channels
        self.history_age = 48
        self.history_limit = 20
