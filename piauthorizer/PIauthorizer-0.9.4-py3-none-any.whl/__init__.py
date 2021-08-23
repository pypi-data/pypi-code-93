if True:
    import os
    for env_variable in [
        "LOG_LEVEL",
        "AUTH_STS_URL",
        "AUTH_ALGORITHM",
        "AUTH_AUDIENCE",
        "AUTH_SCOPE",
        "AUTH_LOGIN_URL",
        "AUTH_JWKS_URL",
        "MODEL_MANAGER_GRANT_TYPE",
        "MODEL_MANAGER_CLIENT_ID",
        "MODEL_MANAGER_CLIENT_SECRET",
        "MODEL_MANAGER_SCOPE",
        "MODEL_MANAGER_LOGIN_URL",
        "STS_APPLICATION_BASIC_URL",
        "STS_APPLICATION_CONFIG_URL",
        "STS_APPLICATION_DEFAULT_TENANT_ID",
        "STS_APPLICATION_DEFAULT_TENANT_NAME",
        "STS_APPLICATION_TENANT_URL"
    ]:
        if os.environ.get(env_variable) is None:
            raise KeyError(f"Environment variable {env_variable} missing.")

from .autorest import *
from .ConfigManager import *
from .functional import *
from .logging import *
