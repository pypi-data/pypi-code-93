from . import v1
from . import v2
from .server import run_simple, make_app, create_app
from .utils import add_server_spec_endpoint

__author__ = """Yossi Mosbacher"""
__email__ = 'joe.mosbacher@gmail.com'
__version__ = '0.1.11'

VERSIONS = {
    "v1": v1,
    "v2": v2,
}

DEFAULT_VERSION = "v2"

def get_server(version, server_spec=False, **kwargs):
    app = VERSIONS[version].app.make_app(**kwargs)
    if server_spec:
        app = add_server_spec_endpoint(app)
    return app

def default_server():
    return get_server(DEFAULT_VERSION)

