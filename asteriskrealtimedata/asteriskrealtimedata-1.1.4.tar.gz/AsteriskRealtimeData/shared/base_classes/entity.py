from dataclasses import dataclass


class Entity:
    _table_name: str

    def get_table_name(self) -> str:
        return self._table_name

