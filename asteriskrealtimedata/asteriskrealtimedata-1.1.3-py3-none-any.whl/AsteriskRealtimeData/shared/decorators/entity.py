class Entity(object):
    def __init__(self, table_name: str):
        self._table_name = table_name

    def __call__(self, wrapped_class, *args, **kwargs):
        def inner_func(*args, **kwargs):
            wrapped_class._table_name = self._table_name
            wrapped_class.get_table_name = self.get_table_name
            return wrapped_class(*args, **kwargs)

        return inner_func

    def get_table_name(self):
        return self._table_name
