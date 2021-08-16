
import os.path
import glob as _glob

def glob(pattern):
    """ Similar to glob.glob, with support for tilde expansion. """
    home = os.path.expanduser('~')
    files = []
    for f in _glob.glob(os.path.expanduser(pattern)):
        if f.startswith(home):
            f = '~' + f[len(home):]
        files.append(f)
    return files

__all__ = ['glob']

