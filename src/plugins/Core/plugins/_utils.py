import json
import os.path

class Json:
    def __init__(self, path: str) -> None:
        self.path = os.path.join("data", path)
        if not os.path.isfile(self.path):
            self.data = {}
        else:
            self.data = json.load(open(self.path, encoding="utf-8"))

    def __setitem__(self, key: str, value: any) -> None:
        if value == None:
            try:
                self.data.pop(str(key))
            except:
                pass
        self.data[str(key)] = value

    def __getattr__(self, item: str) -> any:
        return self.get(item)
    
    def __getitem__(self, key: str) -> any:
        return self.get(key)
    
    def __del__(self) -> None:
        json.dump(self.data, open(self.path, "w", encoding="utf-8"))

    def get(self, key: str, default: any = None) -> None:
        try:
            return self.data[key]
        except:
            if default == None:
                return None
            self.data[key] = default
            return self.get(key, default)

    def items(self):
        return list(self.data.items())

