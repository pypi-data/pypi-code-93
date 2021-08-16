import errno
import json
import os
import warnings
from typing import Dict

from . import _version
from . import base
from . import energy
from . import environment
from . import exceptions

__version__ = _version.get_versions()["version"]


USER_LEVEL_CONFIGURATION_FILE = os.path.expanduser("~/.seedftw/config.json")

__env_var_configuration_loaded = "SEEDFTW_TOKEN_DK_DMI_METOBSAPI_V2"


def __base_configuration() -> Dict:
    return {
        "dmi_metObsAPIv1": "",
        "dmi_metObsAPIv2": "",
    }


def load_configuration(force_reload: bool = False) -> None:
    # Avoiding to reload the configuration if already loaded
    if (force_reload is False) and (
        os.environ.get(__env_var_configuration_loaded) == "1"
    ):
        return
    elif os.path.exists(USER_LEVEL_CONFIGURATION_FILE) is False:
        raise Exception(
            f"The configuration file does not exist ({USER_LEVEL_CONFIGURATION_FILE})"
        )
    else:
        os.environ[__env_var_configuration_loaded] = "1"

    from seedftw.environment.denmark import (
        set_api_token as set_environment_dk_api_token,
    )

    with open(USER_LEVEL_CONFIGURATION_FILE, "r") as fp:
        api_keys_in_file = json.load(fp)

    if api_keys_in_file.get("dmi_metObsAPIv1") is not None:
        set_environment_dk_api_token(
            dmi_metObsAPI=api_keys_in_file.get("dmi_metObsAPIv1")
        )

    if api_keys_in_file.get("dmi_metObsAPIv2") is not None:
        set_environment_dk_api_token(
            dmi_metObsAPIv2=api_keys_in_file.get("dmi_metObsAPIv2")
        )


def create_configuration_file(
    overwrite: bool = False, open_for_edit: bool = False
) -> None:

    if (overwrite is False) and os.path.exists(USER_LEVEL_CONFIGURATION_FILE):
        warnings.warn(
            f"The configuration file already exists ({USER_LEVEL_CONFIGURATION_FILE})"
        )

    else:
        base_config = __base_configuration()

        if not os.path.exists(os.path.dirname(USER_LEVEL_CONFIGURATION_FILE)):
            try:
                os.makedirs(os.path.dirname(USER_LEVEL_CONFIGURATION_FILE))
            except OSError as exc:  # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise

        # Writing to sample.json
        with open(USER_LEVEL_CONFIGURATION_FILE, "w") as outfile:
            outfile.write(json.dumps(base_config, indent=4))

    if open_for_edit:
        os.startfile(USER_LEVEL_CONFIGURATION_FILE, "open")
