"""Application config."""

import os
env = os.environ

def default_endpoint():
    return env.get('SPARSE_DEFAULT_ENDPOINT', 'https://api.sparsedata.net')

def documentation_url():
    return env.get('SPARSE_DOCUMENTATION_URL', 'https://sparsedata.net/docs')

def is_testing():
    return bool(env.get('SPARSE_IS_TESTING', False))

def should_open_browser():
    return bool(env.get('SPARSE_OPEN_BROWSER', False))
