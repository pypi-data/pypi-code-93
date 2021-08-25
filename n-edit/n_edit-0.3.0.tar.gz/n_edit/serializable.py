import json
import typing as t


class Serializable:
    def to_dict(self) -> dict[str, t.Any]:
        raise NotImplemented

    def load_dict(self, dict_: dict[str, t.Any]) -> None:
        raise NotImplemented

    def load_file(self, file_name: str) -> None:
        with open(file_name) as in_file:
            self.load_dict(json.loads(in_file.read()))

    def save_file(self, file_name: str) -> None:
        with open(file_name, "w") as out_file:
            out_file.write(json.dumps(self.to_dict(), indent=4))
