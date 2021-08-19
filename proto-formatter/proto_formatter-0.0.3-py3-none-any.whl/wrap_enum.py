from enum import Enum


class WrapEnum(Enum):
    @classmethod
    def values(cls):
        """
        Get all enum values.
        :return: value list
        """
        return [v.value for name, v in vars(cls).items() if not name.startswith('_') and name != 'values']
