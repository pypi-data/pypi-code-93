# --------------------------------------------------------------- Imports ---------------------------------------------------------------- #

# System
from typing import Optional
import os

# Local
from .filelock import FileLock

# ---------------------------------------------------------------------------------------------------------------------------------------- #



# ------------------------------------------------------------ Public methods ------------------------------------------------------------ #

def save(
    path: str,
    content: str,
    encoding: str = 'utf8',
    debug: bool = False
) -> bool:
    try:
        data = None

        if encoding:
            data = content.encode('utf8')
        else:
            data = content

        with open(path, 'wb') as file:
            file.write(data)

            return True
    except Exception as e:
        if debug:
            print(e)

        return False

def save_sync(
    path: str,
    content: str,
    encoding: str = 'utf8',
    timeout: Optional[float] = None,
    debug: bool = False
) -> bool:
    try:
        with FileLock(path, timeout=timeout):
            return save(path=path, content=content, debug=debug)
    except Exception as e:
        if debug:
            print('ERROR - strio.save_sync(\'{}\')'.format(path), e)

        return False

def load(
    path: str,
    encoding: str = 'utf8',
    debug: bool = False
) -> Optional[str]:
    if not os.path.exists(path):
        if debug:
            print('File at \'{}\' does not exist'.format(path))

        return None

    try:
        with open(path, 'rb') as file:
            binary_content = file.read()

        return binary_content if not encoding else binary_content.decode(encoding)
    except Exception as e:
        if debug:
            print(e)

        return None

def load_sync(
    path: str,
    encoding: str = 'utf8',
    timeout: Optional[float] = None,
    debug: bool = False
) -> Optional[str]:
    try:
        with FileLock(path, timeout=timeout):
            return load(path=path, encoding=encoding, debug=debug)
    except Exception as e:
        if debug:
            print('ERROR - strio.load_sync(\'{}\')'.format(path), e)

        return None

# ---------------------------------------------------------------------------------------------------------------------------------------- #