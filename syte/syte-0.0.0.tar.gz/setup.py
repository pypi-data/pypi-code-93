
from syte import (
    __version__,
    __author__, 
    __license__,
    __desc__,
)

from setuptools import setup, find_packages

setup(
    name = "syte",
    description = __desc__,
    version = __version__,
    author = __author__,
    license = __license__,
    packages = [ p for p in find_packages() if 'test' not in p]
)
