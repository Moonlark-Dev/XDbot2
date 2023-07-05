import json
import os.path


class Json:
    def __init__(self, path: str) -> None:
        self.path = os.path.join("data", path)
        if not os.path.isfile(self.path):
            self.data = {}
        else:
            self.data = json.load(open(self.path, encoding="utf-8"))

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

    def save(self):
        json.dump(self.data, open(self.path, "w", encoding="utf-8"))

    def __del__(self):
        self.save()

    def items(self):
        return list(self.data.items())
