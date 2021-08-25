""" Init file for generating synthetic datasets """

from .synthetic_data import (
    dataset_stats,
    generate_synthetic_dataset,
    write_to_netcdf,
)

from . import time
from . import vertical
