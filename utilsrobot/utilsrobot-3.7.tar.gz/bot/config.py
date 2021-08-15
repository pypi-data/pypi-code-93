import os

class Config(object):
    BOT_TOKEN = os.environ.get("BOT_TOKEN", None)
    API_HASH = os.environ.get("API_HASH", None)
    API_ID = int(os.environ.get("APP_ID", None))
    DB_URI = os.environ.get("DATABASE_URL", None)
    OWNER_ID = int(os.environ.get("OWNER_ID", None))
