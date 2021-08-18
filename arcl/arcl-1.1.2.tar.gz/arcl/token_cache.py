from .config import SAVED_MSAL_TOKEN_CACHE_PATH

from msal_extensions import TokenCache

token_cache = TokenCache(SAVED_MSAL_TOKEN_CACHE_PATH)
