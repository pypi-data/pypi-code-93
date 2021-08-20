"""Classes and functions to interact with a remote QLattice."""
from typing import Dict, List, Optional, Set, Iterable, Union, Callable

import numpy as np
import requests
from pandas import DataFrame

from ._config import DEFAULT_SERVER, Config, resolve_config
from ._httpclient import HttpClient
from ._register import RegisterCollection

from . import _qlnew
from . import _qlold


_USE_V2_API = False


def connect_qlattice(
    qlattice: Optional[str] = None,
    api_token: Optional[str] = None,
    server: str = DEFAULT_SERVER,
    config: Optional[str] = None,
) -> Union[_qlold.QLOld, _qlnew.QLNew]:
    """
    Utility function for connecting to a QLattice. A QLattice (short for Quantum Lattice) is a device which can be used to generate and explore a vast number of models linking a set of input observations to an output prediction. The actual QLattice runs on a dedicated computing cluster which is operated by Abzu. The `feyn.QLattice` class provides a client interface to communicate with, sample models from, and update the QLattice.

    Keyword Arguments:
        qlattice {Optional[str]} -- The qlattice you want to connect to, such as: `a1b2c3d4`. (Should not to be used in combination with the config parameter). (default: {None})
        api_token {Optional[str]} -- Authentication token for the communicating with this QLattice. (Should not to be used in combination with the config parameter). (default: {None})
        server {str} -- The server hosting your QLattice. (Should not to be used in combination with the config parameter). (default: {DEFAULT_SERVER})
        config {Optional[str]} -- The configuration setting in your feyn.ini or .feynrc file to load the url and api_token from. These files should be located in your home folder. (default: {None})

    Returns:
        QLattice -- The QLattice connection handler to your remote QLattice.
    """
    # Config cannot be combined with anything else
    if config and (qlattice or api_token):
        raise ValueError("Must specify either a config or both qlattice and token.")

    # If either qlattice or token specified, then both must be specified.
    if qlattice or api_token:
        if not (qlattice and api_token):
            raise ValueError("Must specify either a config or both qlattice and token.")

    if qlattice:
        cfg = Config(qlattice, api_token, server)
    else:
        cfg = resolve_config(config)

        if cfg is None:
            cfg = _get_community_qlattice_config(server)

    if _USE_V2_API:
        return _qlnew.QLNew(cfg)
    else:
        return _qlold.QLOld(cfg)


def _get_community_qlattice_config(server: str) -> Config:
    resp = requests.post(f"{server}/api/v1/qlattice/community/create", timeout=20)
    resp.raise_for_status()
    data = resp.json()
    print(
        "A new Community QLattice has been allocated for you. This temporary QLattice is available for personal/non-commercial use. "
        "By using this Community QLattice you agree to the terms and conditions which can be found at `https://abzu.ai/privacy`."
    )

    return Config(data["qlattice_id"], data["api_token"], data["server"])
