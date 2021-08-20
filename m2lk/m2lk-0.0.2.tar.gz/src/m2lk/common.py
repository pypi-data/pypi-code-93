import copy
import struct

from collections import OrderedDict
from contextlib import contextmanager
from functools import cached_property
from inspect import ismethod, isclass

from .vars import InterpolationType


class M2FileReader:
    NOT_OPENED_ERROR = 'The file is not opened!'
    ALREADY_OPENED_ERROR = 'The file is already opened!'
    OFFSET_OUT_OF_RANGE = 'File offset is out of range!'

    def __init__(self, filename):
        """
        M2 file reader.
        :param filename: path to the file.
        """
        self.name = filename
        self._fp = None
        self._size = None
        self._format_size_cache = {}

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def open(self):
        if self._fp:
            raise RuntimeError(self.ALREADY_OPENED_ERROR)
        self._fp = open(self.name, mode='rb')

    def close(self):
        if self._fp:
            self._fp.close()
            self._fp = None

    def seek(self, offset):
        if not self._fp:
            raise RuntimeError(self.NOT_OPENED_ERROR)
        if offset >= self.size:
            raise RuntimeError(self.OFFSET_OUT_OF_RANGE)
        self._fp.seek(offset)

    def tell(self):
        return self._fp.tell()

    def read(self, size, offset=None):
        if not self._fp:
            raise RuntimeError(self.NOT_OPENED_ERROR)
        if offset is not None:
            self._fp.seek(offset)
        return self._fp.read(size)

    def unpack(self, dataformat):
        if dataformat not in self._format_size_cache:
            self._format_size_cache[dataformat] = struct.calcsize(dataformat)
        return struct.unpack(dataformat, self.read(self._format_size_cache[dataformat]))

    @property
    def size(self):
        if not self._size:
            if not self._fp:
                raise RuntimeError(self.NOT_OPENED_ERROR)
            offset = self._fp.tell()
            self._size = self._fp.seek(0, 2)
            self._fp.seek(offset)
        return self._size

    @contextmanager
    def safe(self):
        initial_pos = self.tell()
        yield
        self.seek(initial_pos)


class M2Root:
    def __init__(self, reader: M2FileReader, **kwargs):
        self.reader = reader
        super(M2Root, self).__init__(**kwargs)

    @property
    def anim_number(self):
        raise NotImplementedError

    def get_sequence(self, index):
        raise NotImplementedError


class M2Field:
    INDENT = ' '
    NOT_LOADED_ERROR = 'The field is not loaded yet'

    _creation_counter = 0
    dataformat = None
    single = True

    def __new__(cls, *args, **kwargs):
        """
        When a field is instantiated, we store the arguments that were used,
        so that we can present a helpful representation of the object.
        """
        instance = super().__new__(cls)
        instance._args = args
        instance._kwargs = kwargs
        return instance

    def __init__(self, *args, **kwargs):
        self.creation_counter = M2Field._creation_counter
        M2Field._creation_counter += 1

        self.validator = kwargs.pop('validator', None)
        self.field_name = self.parent = self._value = None

    def __deepcopy__(self, memo):
        # Copy field without loaded value if any
        return self.__class__(*copy.deepcopy(self._args), **copy.deepcopy(self._kwargs))

    def __str__(self):
        if not self.loaded:
            return self.__class__.__name__
        return self.to_str()

    @property
    def loaded(self):
        return self._value is not None

    @property
    def value(self):
        if not self.loaded:
            raise RuntimeError(self.NOT_LOADED_ERROR)
        return self._value

    @cached_property
    def root(self):
        if self.parent is None:
            return self
        return self.parent.root

    def bind(self, field_name, parent):
        self.field_name = field_name
        self.parent = parent

    def load(self, reader: M2FileReader):
        if self.dataformat is None:
            raise ValueError('Could not load field value from reader without dataformat')
        value = reader.unpack(self.dataformat)
        if self.single:
            value = value[0]
        self._value = self.validate(value)

    def validate(self, value):
        if self.validator and callable(self.validator):
            value = self.validator(value)
        return value

    def from_json(self, json_value):
        self._value = json_value

    def to_str(self, offset=0):
        return '"{}"'.format(self.value) if isinstance(self.value, str) else str(self.value)


class M2StructMeta(type):
    def __new__(mcs, name, bases, attrs):
        fields = [(fname, attrs.pop(fname)) for fname, obj in list(attrs.items()) if isinstance(obj, M2Field)]
        fields.sort(key=lambda x: x[1].creation_counter)

        # Ensures a base class field doesn't override cls attrs, and maintains
        # field precedence when inheriting multiple parents. e.g. if there is a
        # class C(A, B), and A and B both define 'field', use 'field' from A.
        known = set(attrs)

        def visit(n):
            known.add(n)
            return n

        base_fields = [
            (visit(fname), f)
            for base in bases if hasattr(base, '_declared_fields')
            for fname, f in getattr(base, '_declared_fields').items() if fname not in known
        ]

        attrs['_declared_fields'] = OrderedDict(base_fields + fields)
        return super().__new__(mcs, name, bases, attrs)


class M2Struct(M2Field, metaclass=M2StructMeta):
    def __getattr__(self, item):
        if item in self.fields:
            return self.fields[item]
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{item}'")

    def __getitem__(self, item):
        if item in self.fields:
            return self.fields[item].value
        raise KeyError(f"'{self.__class__.__name__}' object has no item '{item}'")

    @property
    def loaded(self):
        return all(field.loaded for field in self.fields.values())

    @property
    def value(self):
        if self._value is None:
            self._value = OrderedDict((name, field.value) for name, field in self.fields.items())
        return self._value

    @cached_property
    def fields(self):
        """
        A dictionary of {field_name: field_instance}.
        """
        declared_fields = copy.deepcopy(getattr(self, '_declared_fields'))
        fields = OrderedDict()
        for key, field in declared_fields.items():
            fields[key] = field
            field.bind(key, self)
        return fields

    def load(self, reader: M2FileReader):
        """
        Loads fields' values from reader.
        :param reader: M2FileReader instance.
        :return: nothing.
        """
        for name, field in self.fields.items():
            custom_load = f'load_{name}'
            if hasattr(self, custom_load) and ismethod(getattr(self, custom_load)):
                getattr(self, custom_load)(reader)

            field.load(reader)

    def from_json(self, json_value):
        """
        Loads fields' values from json data structure.
        :param json_value: dict {field_name: field_json_value}.
        :return: nothing.
        """
        for name, field in self.fields.items():
            field.from_json(json_value[name])

    def to_str(self, indent=0):
        str_value = self.__class__.__name__ + ': {\n'

        # Collect str values of struct fields
        children_indent = ' ' * (indent + 1)
        for field_name, field in self.fields.items():
            str_value += '{}{}={},\n'.format(children_indent, field_name, field.to_str(indent + 1))

        str_value += ' ' * indent + '}'
        return str_value


class M2Skip(M2Field):
    def __init__(self, size, *args, **kwargs):
        self.size = size
        self._loaded = False
        super(M2Skip, self).__init__(*args, **kwargs)

    @property
    def loaded(self):
        return self._loaded

    def load(self, reader: M2FileReader):
        reader.read(self.size)
        self._loaded = True


class M2Byte(M2Field):
    def load(self, reader: M2FileReader):
        self._value = reader.read(1)[0]


class M2Int16(M2Field):
    dataformat = '<h'


class M2UInt16(M2Field):
    dataformat = '<H'


class M2Int32(M2Field):
    dataformat = '<i'


class M2UInt32(M2Field):
    dataformat = '<I'


class M2Float(M2Field):
    dataformat = '<f'


class M2Fixed16(M2Field):
    dataformat = '<H'

    def validate(self, value):
        return value / 0x7FFF


class M2CompQuat(M2Field):
    dataformat = '<4h'
    single = False

    @staticmethod
    def short_to_float(value):
        if value == -1:
            return 1
        if value > 0:
            value -= 32767
        else:
            value += 32767
        return value / 32767

    def validate(self, value):
        return super(M2CompQuat, self).validate(list(self.short_to_float(x) for x in value))


class M2Range(M2Field):
    dataformat = '<2I'
    single = False


class M2Vector(M2Field):
    single = False

    def __init__(self, size: int, *args, **kwargs):
        self.dataformat = f'<{size}f'
        super(M2Vector, self).__init__(*args, **kwargs)


class M2IntVector(M2Field):
    single = False

    def __init__(self, size: int, *args, **kwargs):
        self.dataformat = f'<{size}i'
        super(M2IntVector, self).__init__(*args, **kwargs)


class M2ByteArray(M2Field):
    def __init__(self, size: int, *args, **kwargs):
        self.size = size
        super(M2ByteArray, self).__init__(*args, **kwargs)

    def __getitem__(self, item: int):
        if not self.loaded:
            raise RuntimeError(self.NOT_LOADED_ERROR)
        if len(self._value) <= item:
            raise IndexError
        return self._value[item]

    def load(self, reader: M2FileReader):
        self._value = list(reader.read(self.size))


class M2FixedString(M2Field):
    def __init__(self, size: int, *args, **kwargs):
        self.size = size
        super(M2FixedString, self).__init__(*args, **kwargs)

    def load(self, reader: M2FileReader):
        self._value = reader.read(self.size).decode()


class M2Bool(M2Field):
    def __init__(self, base_field, *args, **kwargs):
        self.base_field = base_field
        assert isinstance(self.base_field, M2Field), '`base_field` should be an M2Field instance!'
        super(M2Bool, self).__init__(*args, **kwargs)

    def load(self, reader: M2FileReader):
        self.base_field.load(reader)
        self._value = bool(self.base_field.value)


class M2ArrayField(M2Field):
    def __init__(self, base_field, **kwargs):
        assert isinstance(base_field, M2Field), '`base_field` should be an M2Field instance!'
        assert not isclass(base_field), '`base_field` has not been instantiated.'
        self.base_field = base_field

        self._children = None
        super(M2ArrayField, self).__init__(**kwargs)

    def __iter__(self):
        if not self.loaded:
            raise RuntimeError(self.NOT_LOADED_ERROR)
        for child in self._children:
            yield child

    def __getitem__(self, item):
        if not self.loaded:
            raise RuntimeError(self.NOT_LOADED_ERROR)
        return self._children[item]

    def __len__(self):
        if not self.loaded:
            raise RuntimeError(self.NOT_LOADED_ERROR)
        return len(self._children)

    @property
    def loaded(self):
        return self._children is not None

    @property
    def value(self):
        if self._value is None:
            if not self.loaded:
                raise RuntimeError(self.NOT_LOADED_ERROR)
            self._value = list(child.value for child in self._children)
        return self._value

    def load_from(self, reader: M2FileReader, size, offset):
        self._children = []
        if size <= 0 or offset < 0:
            # Nothing to read
            return
        with reader.safe():
            reader.seek(offset)
            for i in range(size):
                child = copy.deepcopy(self.base_field)
                child.bind(str(i), self)
                child.load(reader)
                self._children.append(child)

    def load(self, reader: M2FileReader):
        size, offset = reader.unpack('<2i')
        self.load_from(reader, size, offset)

    def from_json(self, json_value):
        """
        Load M2Array from json data structure.
        :param json_value: list of json values for base_field from_json method.
        :return:
        """
        self._children = []
        for i, val in enumerate(json_value):
            child = copy.deepcopy(self.base_field)
            child.bind(str(i), self)
            child.from_json(val)
            self._children.append(child)


class M2String(M2Field):
    def load(self, reader: M2FileReader):
        size, offset = reader.unpack('<2i')

        self._value = ''
        if size <= 0 or offset < 0:
            # Nothing to read
            return
        with reader.safe():
            reader.seek(offset)
            self._value = reader.read(size).strip(b'\x00').decode()


class M2Box(M2Struct):
    point_a = M2Vector(3)
    point_b = M2Vector(3)


class M2SplineKey(M2Struct):
    def __init__(self, base_field, *args, **kwargs):
        assert isinstance(base_field, M2Field), '`base_field` should be an M2Field instance!'
        assert not isclass(base_field), '`base_field` has not been instantiated.'
        self.base_field = base_field
        super(M2SplineKey, self).__init__(*args, **kwargs)

    @cached_property
    def fields(self):
        fields = OrderedDict()
        for fkey in ['value', 'in_tan', 'out_tan']:
            fields[fkey] = copy.deepcopy(self.base_field)
            fields[fkey].bind(fkey, self)
        return fields


class M2AnimationsField(M2ArrayField):
    def __init__(self, base_field, *args, **kwargs):
        self.base_field = M2ArrayField(base_field)
        self._children = None
        super(M2ArrayField, self).__init__(*args, **kwargs)

    def load(self, reader: M2FileReader):
        root = self.root
        if not isinstance(root, M2Root):
            raise RuntimeError('Could not load animations without an M2Root instance at the root')

        size, offset = reader.unpack('<2i')

        self._children = []
        if size <= 0 or offset < 0:
            return

        # assert size == root.anim_number, 'Animations size should be the same as sequences size!'

        loaded_animations = {}
        with reader.safe():
            reader.seek(offset)
            for i in range(size):
                size, offset = reader.unpack('<2i')

                seq_index, sequence = root.get_sequence(i)
                if seq_index in loaded_animations:
                    self._children.append(self._children[loaded_animations[seq_index]])
                    continue

                child = copy.deepcopy(self.base_field)
                child.bind(str(i), self)

                if sequence.anim_reader:
                    # External source (from .anim file)
                    child.load_from(sequence.anim_reader, size, offset)
                else:
                    # Local source (from .m2 file)
                    child.load_from(reader, size, offset)
                self._children.append(child)
                loaded_animations[seq_index] = i


class M2TrackBaseField(M2Struct):
    interpolation_type = M2UInt16()
    global_sequence = M2Int16()
    timestamps = M2AnimationsField(M2UInt32())

    def to_str(self, indent=0):
        str_value = 'TrackBase<{}, {}>'.format(
            InterpolationType(self['interpolation_type']).name,
            self['global_sequence']
        )
        str_value += '{\n'
        children_indent = ' ' * (indent + 1)
        for i, timestamps in enumerate(self.timestamps):
            if len(timestamps) == 0:
                continue
            str_value += "{}Animation-{}: ".format(children_indent, i)
            str_value += ', '.join("T({})".format(
                self.timestamps[i][j].to_str(indent + 2)
            ) for j in range(len(timestamps)))
            str_value += '\n'

        str_value += ' ' * indent + '}'
        return str_value


class M2TrackField(M2TrackBaseField):
    def __init__(self, base_field, *args, **kwargs):
        self.base_field = base_field
        super(M2TrackField, self).__init__(*args, **kwargs)

    @cached_property
    def fields(self):
        fields = super(M2TrackField, self).fields
        fields['values'] = M2AnimationsField(self.base_field)
        fields['values'].bind('values', self)
        return fields

    def to_str(self, indent=0):
        str_value = 'Track<{}, {}>'.format(
            InterpolationType(self['interpolation_type']).name,
            self['global_sequence']
        )
        str_value += '{\n'
        children_indent = ' ' * (indent + 1)
        for i, timestamps in enumerate(self.timestamps):
            if len(timestamps) == 0:
                continue
            str_value += "{}Animation-{}: ".format(children_indent, i)
            str_value += ", ".join("T({})={}".format(
                self.timestamps[i][j].to_str(indent + 2),
                self.values[i][j].to_str(indent + 2),
            ) for j in range(len(timestamps)))
            str_value += '\n'

        str_value += ' ' * indent + '}'
        return str_value


class M2FakeTrack(M2Struct):
    timestamps = M2ArrayField(M2UInt16())

    def __init__(self, base_field, *args, **kwargs):
        self.base_field = base_field
        super(M2FakeTrack, self).__init__(*args, **kwargs)

    @cached_property
    def fields(self):
        fields = super(M2FakeTrack, self).fields
        fields['values'] = M2ArrayField(self.base_field)
        fields['values'].bind('values', self)
        return fields

    def to_str(self, indent=0):
        str_value = 'FakeTrack{\n'
        str_value += ' ' * (indent + 1) + ', '.join("T({})={}".format(
            self.timestamps[i].to_str(indent + 2),
            self.values[i].to_str(indent + 2)
        ) for i in range(len(self.timestamps)))
        str_value += ' ' * indent + '}'
        return str_value
