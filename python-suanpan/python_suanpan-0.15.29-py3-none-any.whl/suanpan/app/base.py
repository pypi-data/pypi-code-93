# coding=utf-8
from __future__ import absolute_import, print_function

from unittest import mock

from suanpan.log import logger
from suanpan.objects import HasName


class BaseApp(HasName):
    def __call__(self, *args, **kwargs):
        raise NotImplementedError("Method not implemented!")

    def start(self, *args, **kwargs):  # pylint: disable=unused-argument
        logger.info(f"Suanpan component {self.name} start...")

    @property
    def trigger(self):
        raise NotImplementedError(f"{self.name} not support trigger")

    def input(self, argument):
        raise NotImplementedError("Method not implemented!")

    def output(self, argument):
        raise NotImplementedError("Method not implemented!")

    def param(self, argument):
        raise NotImplementedError("Method not implemented!")

    def column(self, argument):
        raise NotImplementedError("Method not implemented!")

    def beforeInit(self, hook):
        raise NotImplementedError("Method not implemented!")

    def afterInit(self, hook):
        raise NotImplementedError("Method not implemented!")

    def beforeCall(self, hook):
        raise NotImplementedError("Method not implemented!")

    def afterCall(self, hook):
        raise NotImplementedError("Method not implemented!")

    def beforeExit(self, hook):
        raise NotImplementedError("Method not implemented!")

    def load(self, *args, **kwargs):
        raise NotImplementedError(f"{self.name} not support load")

    def save(self, *args, **kwargs):
        raise NotImplementedError(f"{self.name} not support save")

    def send(self, *args, **kwargs):
        raise NotImplementedError(f"{self.name} not support send")

    @property
    def args(self):
        raise NotImplementedError(f"{self.name} not support args")

    @property
    def vars(self):
        raise NotImplementedError(f"{self.name} not support args")

    def title(self, title):  # pylint: disable=unused-argument
        return self

    @property
    def modules(self):
        return mock.MagicMock()
