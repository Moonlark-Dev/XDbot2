from . import registry
from ..item import Item
import typing

ItemConstructor = typing.Callable[[int, dict[str, typing.Any], str], Item]

ITEMS: registry.Registry[ItemConstructor] = registry.Registry()