# Copyright 2019-2021 Cambridge Quantum Computing
#
# You may not use this file except in compliance with the Licence.
# You may obtain a copy of the Licence in the LICENCE file accompanying
# these documents or at:
#
#     https://cqcl.github.io/pytket/build/html/licence.html
"""The config module defines a userspace pytket configuration.
The configuration is saved to and loaded from file."""

from .pytket_config import (
    get_config_file_path,
    PytketConfig,
    PytketExtConfig,
    load_config_file,
    write_config_file,
)
