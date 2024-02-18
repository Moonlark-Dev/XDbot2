import typing

T1 = typing.TypeVar("T1")


class ResourceLocation:

    namespace: str
    path: str

    def __init__(self, namespace: str, path: str):
        self.namespace = namespace
        self.path = path

    def getNamespace(self) -> str:
        return self.namespace

    def getPath(self) -> str:
        return self.path

    def __hash__(self) -> int:
        return str(self).__hash__()

    def __str__(self) -> str:
        return f"{self.getNamespace()}:{self.getPath()}"


class Registry(typing.Generic[T1]):

    _map: dict[ResourceLocation, T1]

    def __init__(self):
        self._map = dict()
        self._tagManager = TagManager(self)

    def getTags(self):
        return self._tagManager

    def registry(
        self, location: ResourceLocation, value: T1
    ) -> tuple[ResourceLocation, T1]:
        if location in self._map.keys() or value in self._map.values():
            raise Exception("Duplicate entry")
        self._map[location] = value
        return (location, value)

    def getValue(self, location: ResourceLocation) -> T1:
        return self._map[location]

    def getKey(self, value: T1) -> ResourceLocation:
        for first, second in self._map.items():
            if value == second:
                return first
        raise ValueError(value)

    def getEntries(self) -> list[tuple[ResourceLocation, T1]]:
        entries = list(self._map.items())
        return entries


class TagManager(typing.Generic[T1]):
    _map: dict[ResourceLocation, list[T1]]
    _registry: Registry[T1]

    def __init__(self, registry: Registry[T1]):
        self.registry = registry

    def getEntries(self):
        entries = list(self._map.items())
        return entries

    def getValues(self, location: ResourceLocation) -> list[T1]:
        return self._map[location]

    def getKeys(self, value: T1) -> list[ResourceLocation]:
        keys = list()
        for first, second in self._map.items():
            if value in second:
                keys += first
        return keys

    def put(self, name: ResourceLocation, *args: tuple[T1]):
        for it in args:
            self._map[name].append(it)
        return self

    def contains(self, name: ResourceLocation, value: T1):
        return value in self._map[name]
