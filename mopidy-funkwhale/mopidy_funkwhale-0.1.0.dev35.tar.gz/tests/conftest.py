import pytest

import mopidy_funkwhale.actor
import mopidy_funkwhale.client
import mopidy_funkwhale.library

FUNKWHALE_URL = "https://test.funkwhale"


@pytest.fixture()
def config(tmpdir):
    return {
        "core": {"data_dir": str(tmpdir)},
        "funkwhale": {
            "url": FUNKWHALE_URL,
            "username": "user",
            "password": "passw0rd",
            "cache_duration": 600,
            "client_id": "",
            "client_secret": "",
            "verify_cert": "",
        },
        "proxy": {},
    }


@pytest.fixture
def backend(config):
    return mopidy_funkwhale.actor.FunkwhaleBackend(config=config, audio=None)


@pytest.fixture()
def session(backend):
    return mopidy_funkwhale.client.get_requests_session(
        FUNKWHALE_URL,
        {},
        "test/something",
        base_cls=mopidy_funkwhale.client.SessionWithUrlBase,
    )


@pytest.fixture()
def client(backend, session):
    return backend.client


@pytest.fixture
def library(backend):
    return backend.library
