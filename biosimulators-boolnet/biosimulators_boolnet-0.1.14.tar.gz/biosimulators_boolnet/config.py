""" Configuration for BioSimulators-BoolNet

:Author: Jonathan Karr <karr@mssm.edu>
:Date: 2021-01-08
:Copyright: 2020-2021, Center for Reproducible Biomedical Modeling
:License: MIT
"""

import os

__all__ = ['Config']


class Config(object):
    """ Configuration

    Attributes:
        boolnet_version (:obj:`str`): specific version of BoolNet to use
    """

    def __init__(self):
        self.boolnet_version = os.getenv('BOOLNET_VERSION', None) or None
