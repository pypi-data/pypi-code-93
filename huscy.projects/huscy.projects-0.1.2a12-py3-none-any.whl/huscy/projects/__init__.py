# major.minor.patch.release.number
# release must be one of alpha, beta, rc or final
VERSION = (0, 1, 2, 'alpha', 12)

__version__ = '.'.join(str(x) for x in VERSION)
