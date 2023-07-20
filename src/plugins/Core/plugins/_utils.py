import json
import os.path

class __JsonData__:
    def __init__(self, path: str) -> None:
        self.path = path
        if not os.path.isfile(self.path):
            self.data = {}
        else:
            self.data = json.load(open(self.path, encoding="utf-8"))
    
    def __setitem__(self, key: str, value: any) -> None:
        self.data[str(key)] = value
    
    def get(self, key: str, default: any = None) -> None:
        item = self.data.get(str(key))
        if item is None:
            self.data[key] = default
            return self.get(key, default)
        else:
            return item

    def __del__(self) -> None:
        json.dump(self.data, open(self.path, "w", encoding="utf-8"))

class Json:
    def __init__(self, path: str) -> None:
        self.path = os.path.join("data", path)

    def __getitem__(self, key: str) -> any:
        return self.get(key)

    def get(self, key: str, default: any = None) -> None:
        item = self.data.get(str(key))
        if item is None:
            self.data[key] = default
            return self.get(key, default)
        else:
            return item

    def __setitem__(self, key: str, value: any) -> None:
        self.data[str(key)] = value
        self.save()

    def items(self):
        return list(self.data.items())

    def __getattr__(self, item: str) -> any:
        match item:
            case "data":
                return __JsonData__(self.path)
            case _:
                return self.get(item)
