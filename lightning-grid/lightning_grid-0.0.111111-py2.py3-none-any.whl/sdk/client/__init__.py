import os

import grid.cli.globals as env
from grid.cli.utilities import get_graphql_url
from grid.sdk.auth import Credentials
from grid.sdk.client.grid_gql import gql_client


def create_gql_client(*, websocket: bool = False):
    # since we are manipulating the GRID_URL on the fly, we always need to check the env variable
    url = get_graphql_url(os.environ.get("GRID_URL") or env.DEFAULT_GRID_URL)
    creds = Credentials.from_locale()
    res = gql_client(url=url, creds=creds, websocket=websocket)
    return res
