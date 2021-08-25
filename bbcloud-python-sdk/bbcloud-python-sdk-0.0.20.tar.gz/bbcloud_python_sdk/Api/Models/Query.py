class Query(object):

    def __init__(self):
        self.boot()

    def boot(self):
        self._query = ''
        self._order_by = None
        self._page = 1
        self._page_size = 20

    where_operator_map = {
        '=': 'eq',
        '!=': 'ne',
        '>': 'gt',
        '>=': 'ge',
        '<': 'le',
        '<=': 'lt',
        'like': 'like',
    }

    def has(self, key):
        self._query = '%s%s__has,' % (self._query, key)
        return self

    def whereIn(self, key, value):
        self._query = '%s%s__in=%s,' % (self._query, key, value.split('|'))
        return self

    def whereNotIn(self, key, value):
        self._query = '%s%s__not_in=%s,' % (self._query, key, value.split('|'))
        return self

    def where(self, *args):
        if len(args) == 2:
            self._query = '%s%s=%s,' % (self._query, args[0], args[1])

        elif len(args) == 3:
            self._query = '%s%s__%s=%s,' % (self._query, args[0], self.where_operator_map[args[1]], args[2])

        return self

    def page(self, page=1):
        self._page = page
        return self

    def page_size(self, page_size=20):
        self._page_size = page_size
        return self

    def order_by(self, field, order_by='desc'):
        self._order_by = '%s%s' % ('-' if order_by == 'desc' else '+', field)
        return self
