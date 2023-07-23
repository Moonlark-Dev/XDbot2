from typing import TypedDict


class NbtDict(TypedDict):
    useable: bool
    can_be_sold: bool
    dispoable: bool
    maximum_stack: int
    price: int
    display_name: str
    display_message: str