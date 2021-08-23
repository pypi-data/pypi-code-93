# Copyright 2019 Splunk Inc. All rights reserved.
"""Splunk authentication.conf abstraction module"""

# Custom Libraries
from . import configuration_file


class AuthenticationConfigurationFile(configuration_file.ConfigurationFile):
    """Represents an authentication.conf file"""

    def __init__(self):
        configuration_file.ConfigurationFile.__init__(self)
