__version__ = "0.1.2"

from serifan import session


def api():
    return session.Session()
