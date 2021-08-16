"""

"""


class IteratorMixin:
    base_iterator = list

    def __init__(self):
        self._executed = False
        self._data = self.base_iterator()

    def __iter__(self):
        if not self._executed:
            self._fetch()
        return iter(self._data)

    def __next__(self):
        for item in self:
            yield item

    def _fetch(self, raw=False):
        """
        This is where the _data attribute is filled
        from Cypher query.
        :param bool raw: if True returns non-hydrated result (dict format)
        :return:
        """
        raise NotImplementedError()
