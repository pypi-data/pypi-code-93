"""The ``resilient_exporters`` package provides data exporters designed to be
resilient to peak utilisation and Internet connection disruptions.

Install:

        $ pip install resilient-exporters

"""
import logging
from .exporters import *
from .exceptions import *

# With NullHandler we enable logging only the user sets up logging
logging.getLogger(__name__).addHandler(logging.NullHandler())

pool = ExporterPool([], use_memory=False)
"""Default, ready to use pool of exporter, which uses a file for data storage"""

add_exporter = pool.add_exporter
send = pool.send
