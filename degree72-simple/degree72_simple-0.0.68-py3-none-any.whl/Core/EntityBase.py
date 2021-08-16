class ModelMetaclass(type):

    def __new__(cls,  name,  bases,  attrs):
        field_mappings = dict()

        for k,  v in attrs.items():
            if v is None:
                field_mappings[k] = v

        attrs['__field__mappings__'] = field_mappings

        return type.__new__(cls,  name,  bases,  attrs)


class EntityBase(dict, metaclass=ModelMetaclass):
    def __init__(self, *args, **kwargs):
        super(EntityBase, self).__init__(*args, **kwargs)
        self.__dict__ = self

    @classmethod
    def init_table(cls, table_name):
        cls.__table__ = table_name

    def fields(self):
        fields1 = list(self.__field__mappings__.keys())
        fields2 = list(self.keys())
        for each in fields2:
            if each not in fields1:
                fields1.append(each)
        return fields1


class TestEntity(EntityBase):
    province = None
    store_type = None  # province or private
    site_name = None
    store_id = None  # (given, if exists)
    store_name = None
    licensee_name = None

if __name__ == '__main__':

    t = TestEntity()
    t.hello = '123'
    # print(t.__field__mappings__)
    print(t.fields())