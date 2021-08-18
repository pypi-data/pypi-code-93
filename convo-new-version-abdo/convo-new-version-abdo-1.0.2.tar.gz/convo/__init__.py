import logging

from convo import version

# define the version before the others imports since these need it
__version__ = version.__version__

from convo.run import run
from convo.train import train
from convo.test import test

logging.getLogger(__name__).addHandler(logging.NullHandler())
