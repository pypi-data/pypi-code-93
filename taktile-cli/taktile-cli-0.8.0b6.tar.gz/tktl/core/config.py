import os
from typing import Dict, Optional

from pydantic import BaseSettings


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    LOCAL_STACK: bool = False
    E2E: bool = False
    CI_RUNNER_NAME: Optional[str] = None

    VERBOSE: bool = False
    DEBUG: bool = False
    WEB_URL: str = "https://app.taktile.com"
    TAKTILE_API_URL: str = "https://taktile-api.taktile.com"
    DEPLOYMENT_API_URL: str = "https://deployment-api.taktile.com"

    TKTL_CONFIG_PATH: str = os.path.expanduser("~/.config/tktl")
    CONFIG_FILE_NAME: str = "config.json"
    TAKTILE_API_KEY: Optional[str] = None
    HELP_HEADERS_COLOR: str = "yellow"
    HELP_OPTIONS_COLOR: str = "green"
    USE_CONSOLE_COLORS: bool = True
    HELP_COLORS_DICT: Dict = {
        "help_headers_color": "yellow",
        "help_options_color": "green",
    }

    LOCAL_ARROW_ENDPOINT: str = "grpc+tcp://127.0.0.1:5005"
    LOCAL_REST_ENDPOINT: str = "http://127.0.0.1:8080"
    ARROW_BATCH_MB: int = 50
    PARQUET_BATCH_DEFAULT_ROWS_READ: int = int(1e6)

    FUTURE_ENDPOINTS: bool = False

    class Config:
        case_sensitive = True


settings = Settings()
