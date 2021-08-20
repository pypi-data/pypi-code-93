"""
This module is here to disable the auto-config-resolving logic in the config module,
so that it is easier to tell which config is loaded during test execution.
"""
import feyn._config
import os

UNITTEST_QLATTICE_SERVER = "http://localhost:5000"
UNITTEST_QLATTICE_ID = "test-qlattice"
UNITTEST_API_TOKEN = "secret"


def override_config_resolver():
    feyn._config._config_resolver = _unittest_config_resolver


def _unittest_config_resolver(section):
    if "CI" in os.environ:
        return feyn._config.Config(qlattice=UNITTEST_QLATTICE_ID,
                                   api_token=UNITTEST_API_TOKEN,
                                   server=os.environ["FEYN_QLATTICE_SERVER"])

    return feyn._config.Config(UNITTEST_QLATTICE_ID, UNITTEST_API_TOKEN, UNITTEST_QLATTICE_SERVER)
