import os
from os.path import join, dirname
from dotenv import load_dotenv


def get_env(env_name: str) -> str:
    dotenv_path = join(dirname(__file__), '.env')
    load_dotenv(dotenv_path)

    return os.environ.get(env_name)