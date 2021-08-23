# Copyright 2019 Splunk Inc. All rights reserved.
"""Splunk distsearch.conf abstraction module"""

# Custom Libraries
from . import configuration_file


class DistsearchConfigurationFile(configuration_file.ConfigurationFile):
    """Represents an [distsearch.conf](https://docs.splunk.com/Documentation/Splunk/7.2.0/Admin/Distsearchconf)
    file.
    """

    def __init__(self):
        configuration_file.ConfigurationFile.__init__(self)
