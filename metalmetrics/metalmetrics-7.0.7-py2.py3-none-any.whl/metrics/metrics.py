# -*- coding: utf-8 -*-

from metalmetrics.config.config import ConfigFile
from metalmetrics.metrics.bare import Bare
from metalmetrics.printer.printer import Printer


class MetricsException(Exception):
    def __init__(self, info):
        super().__init__(self)
        self._info = info

    def __str__(self):
        return self._info


class Metrics(object):
    def __init__(self, config):
        if config is None:
            raise MetricsException("config invalid")
        self._config = config
        self._instance = Bare(self._config)
        buf = config.config_file.get(ConfigFile.SPEC, None)
        if buf is None:
            raise MetricsException("spec invalid")
        self._spec = buf.get(Metrics.__name__.lower(), None)
        if self._spec is None:
            raise MetricsException("metrics invalid")

    def _dump(self, data):
        printer = Printer()
        printer.run(data=data, name=self._config.output_file, append=False)

    def routine(self, spec=None):
        specs = []
        if spec is None or len(spec) == 0:
            specs.extend(self._spec)
        else:
            specs.append(spec)
        buf = {}
        ret = {}
        for item in specs:
            ret[item] = self._instance.run(item)
        buf[Metrics.__name__.lower()] = [ret]
        if len(self._config.output_file) != 0:
            self._dump(buf)
        return buf
