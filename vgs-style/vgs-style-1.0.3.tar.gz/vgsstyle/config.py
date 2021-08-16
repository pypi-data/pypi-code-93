from pathlib import Path
from typing import List

import toml
from pydantic import BaseModel, validator


class InvalidConfigException(Exception):
    pass


class MutableConfig(BaseModel):
    exclude: List[str] = None
    application_import_names: List[str] = None

    @validator("exclude", "application_import_names", pre=True)
    def prepare_lists(cls, val):
        if isinstance(val, str):
            return [v.strip() for v in val.split(",")]
        return val


class Config(MutableConfig):
    line_length: int = 88


def load_config() -> Config:
    config_path = Path.cwd() / "pyproject.toml"
    if not config_path.exists():
        return Config()

    try:
        project_config = toml.load(config_path)
    except Exception as exc:
        raise InvalidConfigException(f"Invalid config: {exc}") from exc

    tool_config = project_config.get("tool", {}).get("vgs-style", {})
    try:
        user_config = MutableConfig(**tool_config)
    except TypeError as exc:
        raise InvalidConfigException(str(exc)) from exc

    return Config(**user_config.dict())
