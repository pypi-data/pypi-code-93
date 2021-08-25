# -*- coding: utf-8 -*-

from pip_services3_data.persistence.JsonFilePersister import JsonFilePersister
from ..Dummy import Dummy
from pip_services3_commons.config.ConfigParams import ConfigParams
from pip_services3_commons.errors.ConfigException import ConfigException


class TestJsonFilePersister:

    @classmethod
    def setup_class(cls):
        cls._persister = JsonFilePersister(Dummy)

    def test_configure_with_no_path_key(self):
        try:
            self._persister.configure(ConfigParams())
        except Exception:
            assert Exception is not None
            assert isinstance(Exception, ConfigException)

    def test_configure_if_path_key_check_property(self):
        file_name = '../test_JsonFilePersister'
        self._persister.configure(ConfigParams.from_tuples('path', file_name))
        assert file_name == self._persister.path
