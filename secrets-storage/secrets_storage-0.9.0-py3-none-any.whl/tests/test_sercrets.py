import abc
from dataclasses import dataclass

import pytest

from secrets_storage import BaseStorage, ENVStorage, Secrets


class TestSecrets:
    def test_if_not_found_storage(self):
        secrets = Secrets(storages=[])
        with pytest.raises(ValueError):
            secrets.get("DEMO")

    def test_if_all_storages_disable(self):
        secrets = Secrets(storages=[ENVStorage(available=False)])
        with pytest.raises(ValueError):
            secrets.get("DEMO")


def test_base_storage():
    BaseStorage.__abstractmethods__ = set()

    @dataclass
    class DummyStorage(BaseStorage):
        name: str
        available: bool

    dummy_storage = DummyStorage(name="dummy_storage", available=True)
    assert isinstance(BaseStorage, abc.ABCMeta)
    assert dummy_storage.enabled is None
    assert dummy_storage.get_secret(name="test") is None
