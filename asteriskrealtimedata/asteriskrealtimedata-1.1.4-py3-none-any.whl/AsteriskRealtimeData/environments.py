import os
from antidote import Constants, const


class Config(Constants):
    HOST = const[str](os.environ.get("MONGODB_HOST", "127.0.0.1"))
    PORT = const[int](os.environ.get("MONGODB_PORT", 27017))
    DATABASE = const[str](os.environ.get("MONGODB_DATABASE", "test_asterisk"))
    USER = const[str]("")
    PASSWORD = const[str]("")
