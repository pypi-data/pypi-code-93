# Copyright 2019 Splunk Inc. All rights reserved.
"""Splunk transforms.conf abstraction module"""

# Custom Libraries
from . import configuration_file


class TransformsConfigurationFile(configuration_file.ConfigurationFile):
    """Represents a [transforms.conf](http://docs.splunk.com/Documentation/Splunk/latest/Admin/Transformsconf) file."""

    def __init__(self):
        configuration_file.ConfigurationFile.__init__(self)
