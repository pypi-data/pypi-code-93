# -*- coding: utf-8 -*-

import abc


class MetricsAbstract(abc.ABC):
    def __init__(self, config):
        self._config = config

    @abc.abstractmethod
    def _execution(self, spec):
        pass

    def run(self, spec):
        return self._execution(spec)
