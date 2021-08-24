import os


def get_bool(key, default):
    v = os.environ.get(key, default)
    if v in ["False", "0", False]:
        return False
    else:
        return True


class Config:
    FRONTEGG_URL = os.environ.get("FRONTEGG_SUPERWISE_URL", "https://auth.superwise.ai")
    SUPERWISE_HOST = os.environ.get("SUPERWISE_HOST", "portal.superwise.ai")
    POOLING_INTERVAL_SEC = 15
    DEBUG = get_bool("DEBUG", "False")
    LIST_DROP_DATA_COLS = ["task_id", "version_id"]
