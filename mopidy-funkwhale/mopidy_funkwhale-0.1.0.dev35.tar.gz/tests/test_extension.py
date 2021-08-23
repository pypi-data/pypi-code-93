from __future__ import unicode_literals

import mopidy_funkwhale


def test_get_default_config():
    ext = mopidy_funkwhale.Extension()

    config = ext.get_default_config()

    assert "[funkwhale]" in config
    assert "enabled = true" in config
    assert "url = https://demo.funkwhale.audio" in config
    assert "username =" in config
    assert "password =" in config
    assert "client_id =" in config
    assert "client_secret =" in config
    assert "verify_cert =" in config


def test_get_config_schema():
    ext = mopidy_funkwhale.Extension()

    schema = ext.get_config_schema()
    assert "url" in schema
    assert "username" in schema
    assert "password" in schema
    assert "cache_duration" in schema
