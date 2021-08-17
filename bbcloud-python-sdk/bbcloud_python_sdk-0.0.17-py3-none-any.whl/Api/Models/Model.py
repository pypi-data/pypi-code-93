import copy

from bbcloud_python_sdk.Api import BBCloud
from bbcloud_python_sdk.Api.Models.Query import Query


class Model(Query):

    def __init__(self, *args, **kwargs):
        super(Model, self).__init__()
        self.boot()
        self.loader(args[0] if args else kwargs)

    def __str__(self):
        model_str = '%s {\n' % self.__class__
        for k in self._attributes:
            model_str = model_str + "  '%s':'%s'\n" % (k, self._attributes[k])
        model_str = model_str + '}\n'
        return model_str

    def __repr__(self):
        return str('%s #%s' % (self.__class__, self.id))

    def __getattr__(self, attribute):
        try:
            return self.__dict__['_attributes'][attribute]
        except KeyError:
            raise AttributeError("'%s' object has no attribute '%s'" % (self.__class__.__name__, attribute))

    def __setattr__(self, key, value):
        if key in self.__dict__.get('_attributes', {}) and key != 'id':
            self.__dict__['_attributes'][key] = value
            self.__dict__['_changes'][key] = value
        else:
            super().__setattr__(key, value)

    def to_dict(self):
        return self._attributes

    def get_query(self):
        return {
            'q': self._query,
            'page': self._page,
            'page_size': self._page_size,
            'order_by': self._order_by
        }

    def get_modal_path(self):
        try:
            return getattr(self, '_modal_path')
        except AttributeError:
            model_name = self.__class__.__name__.lower()
            return '%s/%ss' % (model_name, self.__class__.__name__.lower())

    def reflection(self, data):
        if data:
            new_object = copy.deepcopy(self)
            new_object.boot()
            return new_object.loader(data)

    def boot(self):
        super(Model, self).boot()

        self._protocol = BBCloud.protocol
        # The model's attributes.
        self._attributes = {}
        # The model attribute's original state.
        self._original = {}
        # The changed model attributes.
        self._changes = {}

    def loader(self, data):
        self._attributes = data
        self._original = data
        return self

    def _get_key(self):
        return self.id if hasattr(self, 'id') else None

    def get(self):
        items = []
        data = BBCloud.protocol.set_request_query(
            query=self.get_query()
        ).set_request_path(
            request_path=self.get_modal_path()
        ).get()
        for item in data:
            items.append(self.reflection(data=item))
        return items

    def find(self, id):
        return self.where('id', id).first()

    def first(self):
        res = self.page(1).page_size(1).get()
        if res and len(res) >= 1:
            return res[0]
        else:
            return None

    def create(self, data=None):

        if not data:
            data = self._attributes

        if 'id' in data:
            data.pop('id')

        res = self._protocol.set_request_path(
            request_path=self.get_modal_path()
        ).create(data)

        return self.reflection(data=res)

    def save(self):
        key = self._get_key()
        if key:
            return self._protocol.set_request_path(
                request_path=self.get_modal_path()
            ).patch(id=key, data=self._changes)

    def delete(self):
        key = self._get_key()
        if key:
            return self._protocol.set_request_query(
                query=self._query
            ).set_request_path(
                request_path=self.get_modal_path()
            ).delete(id=key)
        else:
            items = self.get()
            res = []
            for item in items:
                res.append(item.delete())
            return all(res)
