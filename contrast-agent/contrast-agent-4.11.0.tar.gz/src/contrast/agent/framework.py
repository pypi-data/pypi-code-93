# -*- coding: utf-8 -*-
# Copyright © 2021 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from pip._vendor import pkg_resources
from collections import namedtuple

from contrast.agent import scope
from contrast.extern import structlog as logging

logger = logging.getLogger("contrast")

Version = namedtuple("Version", ["major", "minor", "patch"])
SUPPORTED_FRAMEWORKS = ["django", "falcon", "flask", "pyramid"]
DEFAULT_FRAMEWORK = "WSGI"


class Framework(object):
    """
    A class to store information about the
    current web framework used for an application
    """

    def __init__(self):
        self._name = ""
        self.version = None
        self.set_info()

    @property
    def name(self):
        return self._name.capitalize()

    @property
    def name_lower(self):
        return self._name.lower()

    @property
    def full_version(self):
        return "{}.{}.{}".format(
            self.version.major, self.version.minor, self.version.patch
        )

    def set_info(self):
        framework = self.discover_framework()

        if framework:
            version = framework.version.split(".")
            patch = version[2] if len(version) > 2 else "0"
            self.version = Version(major=version[0], minor=version[1], patch=patch)
            self._name = framework.project_name
        else:
            logger.debug(
                "Did not find the current framework. Assuming it's %s.",
                DEFAULT_FRAMEWORK,
            )
            self._name = DEFAULT_FRAMEWORK
            self.version = Version(major="0", minor="0", patch="0")

    def discover_framework(self):
        """
        Except in the agent's own testing environment, the assumption here is that all environments
        using the agent will have only one supported framework.

        :return pkg_resources.DistInfoDistribution instance
        """
        with scope.contrast_scope():
            # Enter scope to prevent a recursive bug in pkg_resources which
            # calls on our re_patch and attempts to re-initialize this class.
            for framework_name in SUPPORTED_FRAMEWORKS:
                try:
                    return pkg_resources.get_distribution(framework_name)
                except Exception:
                    continue

        return None

    def __repr__(self):
        return "{} {}".format(self.name, self.full_version)
