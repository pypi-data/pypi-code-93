__version__ = "0.1.0"

from serifan import session


def api():
    return session.Session()
