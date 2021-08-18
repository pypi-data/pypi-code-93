import logging

import convo

from convo.core.train import train
from convo.core.visualize import visualize

logging.getLogger(__name__).addHandler(logging.NullHandler())

__version__ = convo.__version__
