# -*- coding: utf-8 -*-
"""
    binalyzer_core.data_provider
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    This module implements basic data providers for binary streams.

    :copyright: 2021 Denis Vasilík
    :license: MIT
"""
import io


class DataProviderBase(object):
    @property
    def data(self):
        pass

    @data.setter
    def data(self, value):
        pass

    def read(self, template):
        pass

    def write(self, template, value):
        pass


class DataProvider(DataProviderBase):
    def __init__(self, data):
        self._data = data

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value):
        self._data = value

    def read(self, template):
        absolute_address = template.absolute_address
        size = template.size
        self.data.seek(absolute_address)
        value = self.data.read(size)
        self.data.seek(0)
        return value

    def write(self, template, value):
        self.data.seek(template.absolute_address)
        self.data.write(value)
        self.data.seek(0)


class BufferedIODataProvider(DataProvider):

    def __init__(self, size=0, value=0):
        self._value = value
        super(BufferedIODataProvider, self).__init__(
            io.BytesIO(bytes([value] * size)))


class ZeroedDataProvider(BufferedIODataProvider):
    def __init__(self, size=0):
        super(ZeroedDataProvider, self).__init__(size, 0)


class PinnedBufferedIODataProvider(BufferedIODataProvider):
    def __init__(self, size=0, value=0, address=0):
        self._address = address
        super(PinnedBufferedIODataProvider, self).__init__(size, value)

    def read(self, template):
        self.extend(template)
        self.data.seek(self._address)
        return self.data.read(template.size)

    def write(self, template, value):
        self.data.seek(self._address)
        self.data.write(value)

    def extend(self, template):
        data_size = self.data.seek(0, 2)
        if template.size > data_size:
            extension_size = template.size - data_size
            self.data.write(bytes([self._value] * extension_size))
