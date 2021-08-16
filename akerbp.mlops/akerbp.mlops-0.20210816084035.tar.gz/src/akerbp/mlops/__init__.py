from importlib.metadata import version
try:
    __version__ = version('akerbp.mlops')
except:
   __version__ = 'unknown' 