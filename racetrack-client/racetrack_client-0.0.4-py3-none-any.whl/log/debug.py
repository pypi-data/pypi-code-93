import os


def debug_endpoints_enabled() -> bool:
    return os.environ.get('DEBUG_ENDPOINTS', '').lower() in {'true', 't', 'yes', 'y', '1'}
