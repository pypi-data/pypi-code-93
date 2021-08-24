import json


class DBInterface:
    def __insert__(self, *args, **kwargs):
        raise NotImplementedError

    def __select__(self, *args, **kwargs):
        raise NotImplementedError


class SDB:

    @staticmethod
    def __load__(path, table_name):
        try:
            with open(f"{path}{table_name}.json", "r") as f:
                return json.load(f)
        except Exception as e:
            return {}

    @staticmethod
    def __write__(data, path, table_name):
        with open(f"{path}{table_name}.json", "w") as f:
            json.dump(data, f, ensure_ascii=False)


class JsonDBInterface(DBInterface, dict):
    def __init__(self, table_name, path="./"):
        super().__init__()
        self.path = path
        self.table_name = table_name
        self.update(SDB.__load__(path=path, table_name=table_name))

    def dump(self):
        SDB.__write__(self.__dict__, self.path, self.table_name)

    def __insert__(self, key, value, e=RuntimeError()):
        if key in self.keys():
            raise e
        else:
            self.__setitem__(key, value)
            self.dump()

    def __select__(self, key):
        if key not in self.keys():
            return None
        else:
            return self.__getitem__(key)

    def __update__(self, key, value):
        self.__setitem__(key, value)
        self.dump()

    def __delete__(self, key):
        self.__delitem__(key)
        self.dump()