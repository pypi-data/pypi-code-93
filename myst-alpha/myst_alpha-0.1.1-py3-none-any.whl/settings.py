import pathlib
from typing import Optional

import pydantic

PROJECT_ROOT = pathlib.Path(__file__).parent.parent.absolute()


class Settings(pydantic.BaseSettings):
    """Runtime settings for the Myst client."""

    MYST_APPLICATION_CREDENTIALS: Optional[pathlib.Path]

    @pydantic.validator("MYST_APPLICATION_CREDENTIALS")
    def validate_service_account_key_path(cls, v: Optional[str]) -> Optional[pathlib.Path]:
        """Makes sure the service account key is a valid path."""
        if isinstance(v, str):
            return pathlib.Path(v)
        elif v is None:
            return None
        else:
            raise pydantic.ValueError(
                "`MYST_APPLICATION_CREDENTIALS` must be a string if set.",
            )


settings = Settings()
