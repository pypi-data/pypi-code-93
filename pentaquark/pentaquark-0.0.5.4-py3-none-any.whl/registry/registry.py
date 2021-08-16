import enum


class RegistryConstants(enum.Enum):
    OVERRIDE = "OVERRIDE"
    SKIP = "SKIP"
    RAISE = "RAISE"


class Registry:
    def __init__(self):
        self._registry = {}

    def add(self, key, value, if_exists=RegistryConstants.OVERRIDE):
        if key in self._registry:
            if if_exists == RegistryConstants.SKIP:
                return
            if if_exists == RegistryConstants.RAISE:
                raise ValueError(f"'{key}' already in registry")
        self._registry[key] = value

    def clear(self):
        self._registry.clear()

    def __getitem__(self, item):
        return self._registry[item]

    def __contains__(self, item):
        return item in self._registry

    def items(self):
        return self._registry.items()

    def get(self, item, default=None):
        try:
            return self[item]
        except KeyError:
            return default
