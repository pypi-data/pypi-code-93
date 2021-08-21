import os

from pydantic import BaseSettings


class Settings(BaseSettings):

    HOME_PATH = os.path.expanduser('~/.architect/')
    DEFAULT_BACKEND_TYPE: str = 'local'


settings = Settings()
