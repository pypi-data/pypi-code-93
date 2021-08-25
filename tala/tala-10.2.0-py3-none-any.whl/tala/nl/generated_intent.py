from collections import OrderedDict
from itertools import chain

from tala.utils.equality import EqualityMixin


class GeneratedIntent(EqualityMixin):
    def __init__(self, name, samples):
        self._name = name
        self._samples = samples

    @property
    def name(self):
        return self._name

    @property
    def samples(self):
        return self._samples


class GeneratedBuiltinRequestIntent(GeneratedIntent):
    @property
    def name(self):
        return f"request:{self._name}"


class GeneratedBuiltinReportIntent(GeneratedIntent):
    @property
    def name(self):
        return f"report:{self._name}"


class GeneratedBuiltinAnswerIntent(GeneratedIntent):
    @property
    def name(self):
        return f"answer:{self._name}"


class GeneratedCustomIntent(GeneratedIntent):
    def __init__(self, name, sources, samples):
        super().__init__(name, samples)
        self._sources = sources

    @property
    def required_entities(self):
        lists = [source.required_entities for source in self._sources]
        all_entities = chain(*lists)
        unique_entities = list(OrderedDict.fromkeys(all_entities))
        return unique_entities
