import os

if True:
    for env_variable in [
        "LOG_LEVEL",
        "MODEL_MANAGER_GRANT_TYPE",
        "MODEL_MANAGER_CLIENT_ID",
        "MODEL_MANAGER_CLIENT_SECRET",
        "MODEL_MANAGER_SCOPE",
        "MODEL_MANAGER_CONTAINER",
        "MODEL_MANAGER_LOGIN_URL",
        "MODEL_MANAGER_GET_FILES_URL",
        "MODEL_MANAGER_DOWNLOAD_FILE_URL",
        "STS_APPLICATION_DEFAULT_TENANT_NAME"
    ]:
        if os.environ.get(env_variable) is None:
            raise KeyError(f"Environment variable {env_variable} missing.")

from PIModelManager.model_manager import ModelManager
