
from __future__ import print_function
import sys
import decimal
from dateutil.parser import parse as date_parse
from generateDS import AnyTypeIdentifier, mapName, cleanupName


#
# Globals
ExternalEncoding = ''
options = None

# This variable enables users (modules) that use this module to
# check to make sure that they have imported the correct version
# of generatedssuper.py.
Generate_DS_Super_SA_ = None

#
# Tables of builtin types
Simple_type_table = {
    'string': None,
    'normalizedString': None,
    'token': None,
    'base64Binary': None,
    'hexBinary': None,
    'integer': None,
    'positiveInteger': None,
    'negativeInteger': None,
    'nonNegativeInteger': None,
    'nonPositiveInteger': None,
    'long': None,
    'unsignedLong': None,
    'int': None,
    'unsignedInt': None,
    'short': None,
    'unsignedShort': None,
    'byte': None,
    'unsignedByte': None,
    'decimal': None,
    'float': None,
    'double': None,
    'boolean': None,
    'duration': None,
    'dateTime': None,
    'date': None,
    'time': None,
    'gYear': None,
    'gYearMonth': None,
    'gMonth': None,
    'gMonthDay': None,
    'gDay': None,
    'Name': None,
    'QName': None,
    'NCName': None,
    'anyURI': None,
    'language': None,
    'ID': None,
    'IDREF': None,
    'IDREFS': None,
    'ENTITY': None,
    'ENTITIES': None,
    'NOTATION': None,
    'NMTOKEN': None,
    'NMTOKENS': None,
}
sorted_type_table = dict(
    SmallInteger=(
        set(('short', 'unsignedShort', )),
        None,
        lambda x: int(x) if x else None,
    ),
    Integer=(
        set((
            'integer', 'positiveInteger', 'negativeInteger', 
            'nonNegativeInteger', 'nonPositiveInteger', 
            'int', 'unsignedInt', 
        )),
        None,
        lambda x: int(x) if x else None,
    ),
    BigInteger=(
        set(('long', 'unsignedLong', )),
        None,
        lambda x: long(x) if x else None,
    ),
    Numeric=(
        set(('decimal', )),
        None,
        lambda x: decimal.Decimal(x) if x else None,
    ),
    Float=(
        set(('float', 'double', )),
        None,
        lambda x: float(x) if x else None,
    ),
    Unicode=(
        set((
            'string', 'normalizedString', 'token', 'NCName', 
            'ID', 'IDREF', 'IDREFS', 'ENTITY', 'ENTITIES', 'NOTATION',
            'NMTOKEN', 'NMTOKENS', 'QName', 'anyURI', 'base64Binary',
            'hexBinary', 'Name', 'language',
            'duration', 'gYear', 'gYearMonth', 'gMonth', 'gMonthDay', 'gDay', 
        )),
        'Unicode(1000)',
        lambda x: unicode(x),
    ),
    UnicodeText=(
        set((
        )),
        None,
        lambda x: unicode(x),
    ),
    Date=(
        set(('date', )),
        None,
        lambda x: date_parse(x).date() if x else None
    ),
    DateTime=(
        set(('dateTime', )),
        None,
        lambda x: date_parse(x) if x else None
    ),
    Time=(
        set(('time', )),
        None,
        lambda x: date_parse(x).time() if x else None
    ),
    Boolean=(
        set(('boolean', )),
        None,
        lambda x: (int(x) != 0 if x.isdigit() else (x == 'true')) if x else None,
    ),
)


#
# Classes

class GeneratedsSuper(object):
    def gds_format_string(self, input_data, input_name=''):
        return input_data

    def gds_format_integer(self, input_data, input_name=''):
        return '%d' % input_data

    def gds_format_float(self, input_data, input_name=''):
        return '%f' % input_data

    def gds_format_double(self, input_data, input_name=''):
        return '%e' % input_data

    def gds_format_boolean(self, input_data, input_name=''):
        return '%s' % input_data

    def gds_str_lower(self, instring):
        return instring.lower()

    def buildSA(self, node, models_, session_, buildobj_):
        already_processed = set()
        attrib = find_attr_value_(node)
        if attrib is None:
            return
        self.buildAttributesSA(
            node, attrib, models_, session_, buildobj_, already_processed)
        supermod = self.__class__.supermod_
        seq = node #lxml
        if hasattr(node, 'childNodes'): #minidom
            seq = [
                child for child in node.childNodes \
                if child.nodeType == child.ELEMENT_NODE
            ]
        for child in seq:
            tag = None
            if hasattr(child, 'tag'): #lxml/etree
                tag = child.tag
            elif hasattr(child, 'nodeName'): #minidom
                tag = child.nodeName
            if not tag:
                continue
            nodeName_ = supermod.Tag_pattern_.match(tag).groups()[-1]
            self.buildChildrenSA(
                child, node, nodeName_, models_, session_, buildobj_)
        return self

    def buildAttributesSA(
            self, node, attrs, models_, session_, buildobj_, already_processed):
        result = dict()
        cls = self.__class__
        columns = cls.columns()
        for spec in self.member_data_items_:
            name = cls.clean_name(spec.get_name())
            sa_attrs = columns[name]

            clean_data_type = sa_attrs['clean_data_type']
            data_type = sa_attrs['data_type']

            if data_type in Simple_type_table:

                sa_type = sa_attrs['sa_type']
                if sa_type in sorted_type_table:
                    table, alias, parser = sorted_type_table[sa_type]

                    value = find_attr_value_(node, name)
                    if value is not None and name not in already_processed:
                        already_processed.add(name)
                        try:
                            value = parser(value)
                            if buildobj_:
                                setattr(self, name, value)
                        except ValueError as exp:
                            raise_parse_error(node, 'Bad %s attribute: %s' % (
                                sa_type, exp, ))
                    result[name] = value

                else:
                    sys.stderr.write('Unhandled simple type: %s %s\n' % (
                        name, data_type, ))
            else:
                pass
        
        model = models_.get(cls.model_name(full=True))

        pk_ = cls.pk()
        instance = None

        if pk_ in result:
            query = session_.query(model).filter_by(**{pk_: result[pk_]})
            instance = query.first()
        if instance is None:
            instance = model(**result)
            if instance:
                session_.add(instance)
        else:
            for k, v in result.iteritems():
                setattr(instance, k, v)
        self.instance = instance

    def buildChildrenSA(
            self, child_, node, nodeName_, models_, session_, buildobj_, 
            fromsubclass_=False):
        supermod = self.__class__.supermod_
        try:
            child_class = getattr(supermod, nodeName_)
        except AttributeError:
            # the suffix is defined in process_includes.py
            child_class = getattr(supermod, nodeName_ + 'Type') 
        obj_ = child_class.factory()
        obj_.buildSA(child_, models_, session_, buildobj_)
        if buildobj_:
            setattr(self, nodeName_, obj_)
        obj_.original_tagname_ = nodeName_

        spec = self.fields_idx[nodeName_]
        child_attrs = spec.get_child_attrs()
        maxOccurs = child_attrs.get(u'maxOccurs', '')
        maxOccurs = int(maxOccurs) if maxOccurs.isdigit() else 99999
        if maxOccurs == 1:
            objpk = getattr(obj_.instance, child_class.pk())
            setattr(self.instance, nodeName_, objpk)
        elif maxOccurs > 1:
            getattr(self.instance, nodeName_).append(obj_.instance)

    @staticmethod
    def gds_encode(instring):
        if sys.version_info.major == 2:
            if ExternalEncoding:
                encoding = ExternalEncoding
            else:
                encoding = 'utf-8'
            return instring.encode(encoding)
        else:
            return instring

    @classmethod
    def get_prefix_name(cls, tag):
        prefix = ''
        name = ''
        items = tag.split(':')
        if len(items) == 2:
            prefix = items[0]
            name = items[1]
        elif len(items) == 1:
            name = items[0]
        return prefix, name

    @classmethod
    def generate_column_(cls, wrtmodels, name, data_type, **opts):
        column = cls.build_column_(name, data_type, **opts)
        wrtmodels("    %s = %s\n" % (name, column))

    @classmethod
    def generate_secondary_(
            cls, wrtsecondary, name, cls1, cls2):
        fk1 = cls.build_fk_(
            cls1,
            onupdate="CASCADE",
            ondelete="CASCADE",
        )
        col1 = cls.build_column_(
            None, fk1, '%s_id' % cls1.table_name(), primary_key=True)
        fk2 = cls.build_fk_(
            cls2,
            onupdate="CASCADE",
            ondelete="CASCADE",
        )
        col2 = cls.build_column_(
            None, fk2, '%s_id' % cls2.table_name(), primary_key=True)
        secondary = "%s_table = sa.Table(\n    '%s%s', metadata,\n" % (
            name, options.table_prefix_, name, )
        secondary += "    %s,\n    %s\n)\n" % (
            col1, col2, )
        wrtsecondary('%s\n' % secondary)

    @classmethod
    def build_column_(cls, name, data_type, sqlname=None, **opts):
        if name == cls.pk():
            opts.update(
                primary_key=True,
                nullable=False,
            )
        if sqlname is None:
            sqlname = cls.unique_field_map.get(name)
        opts = (',\n        **' + repr(opts)) if opts else ''
        return "sa.Column(\n        '%s', %s%s)" % (
            sqlname, data_type, opts, )

    @classmethod
    def build_fk_(cls, target_cls, **opts):
        sqlpk = target_cls.unique_field_map.get(target_cls.pk())
        target = '%s.%s' % (
            target_cls.table_name(), sqlpk, )
        opts.update(
            deferrable=True, initially='DEFERRED', )
        opts = (',\n            **%s' % repr(opts)) if opts else ''
        return '\n        sa.ForeignKey(\n            "%s"%s\n        )' % (
            target, opts, )

    @classmethod
    def clean_name(cls, name):
        prefix, name = cls.get_prefix_name(name)
        return mapName(cleanupName(name))

    @classmethod
    def index_spec(cls):
        cls.fields_idx = dict([ #ordereddict
            (cls.clean_name(spec.get_name()), spec) \
            for spec in cls.member_data_items_
        ])

    @classmethod
    def init_fields_(cls, supermod_, modtypes_):
        cls.supermod_ = supermod_
        pk_ = cls.pk()
        cls.index_spec()
        fields_idx = cls.fields_idx.keys()
        if sys.version_info.major == 3:
            fields_idx = list(fields_idx)
        if cls.superclass:
            fields_idx.append(cls.superclass.model_name())
        if cls.subclass:
            fields_idx.append(cls.subclass.model_name())
        if cls.fields_idx and pk_ and pk_ not in cls.fields_idx:
            fields_idx.append(pk_)
        cls.unique_field_map = make_unique_name_map(fields_idx)

        cols_attrs = dict()
        
        # detect sa type
        for spec in cls.member_data_items_:
            sa_name = cls.clean_name(spec.get_name())
            
            child_attrs = spec.get_child_attrs() or dict()
            data_type = spec.get_data_type()
            prefix, data_type = cls.get_prefix_name(data_type)
            if data_type in modtypes_.Defined_simple_type_table:
                data_type = modtypes_.Defined_simple_type_table[data_type]
                prefix, data_type = cls.get_prefix_name(data_type.type_name)
            clean_data_type = mapName(cleanupName(data_type))
            if data_type == AnyTypeIdentifier:
                data_type = 'string'
            
            opts = dict()
            if spec.get_optional():
                opts['nullable'] = True

            sa_data = dict(
                sa_name=sa_name,
                sqlname=cls.unique_field_map.get(sa_name),
                clean_data_type=clean_data_type,
                data_type=data_type,
                options=opts,
            )
            
            if data_type in Simple_type_table:
            
                sa_type = 'UnicodeText'
                if sys.version_info.major == 2:
                    sorted_type_table_items = sorted_type_table.iteritems()
                else:
                    sorted_type_table_items = sorted_type_table.items()
                for key, value in sorted_type_table_items:
                    table, alias, parser = value
                    if data_type in table:
                        sa_type = key
                        break
                else:
                    sys.stderr.write('Unhandled simple type: %s %s\n' % (
                        sa_name, data_type, ))
                sa_data.update(
                    sa_type=sa_type,
                )
            
            else:
            
                minOccurs = child_attrs.get(u'minOccurs', '')
                minOccurs = int(minOccurs) if minOccurs.isdigit() else 0
                maxOccurs = child_attrs.get(u'maxOccurs', '')
                maxOccurs = int(maxOccurs) if maxOccurs.isdigit() else 99999
                sa_data.update(
                    minOccurs=minOccurs,
                    maxOccurs=maxOccurs,
                )
            
            cols_attrs[sa_name] = sa_data
        cls.set_columns(cols_attrs)

    @classmethod
    def attrs(cls):
        return cls.supermod_.__sa_attrs__[cls.__name__]

    @classmethod
    def model_name(cls, full=False):
        name = cls.attrs()['model_name']
        if full:
            name += options.class_suffixes
        return name

    @classmethod
    def columns(cls):
        return cls.attrs()['columns']

    @classmethod
    def info(cls):
        return cls.attrs()['info']

    @classmethod
    def set_columns(cls, columns):
        cls.attrs()['columns'] = columns

    @classmethod
    def table_name(cls):
        return cls.attrs()['table_name']

    @classmethod
    def pk(cls):
        return options.pk_.get(
            cls.model_name(), 
            cls.attrs().get(
                'pk',
                options.pk_.get(''))
            )

    @classmethod
    def generate_model_(cls, wrtmodels, wrtsecondary):
        info = cls.info()
        if not info.get('generate', True):
            return
        model_name = cls.model_name()
        columns = cls.columns()
        
        wrtmodels('\nclass %s(DeclarativeBase):\n' % cls.model_name(full=True))
        wrtmodels('    __tablename__ = "%s"\n' % cls.table_name())
        
        if cls.superclass is not None: # table inheritance pg??
            fk = cls.build_fk_(
                cls.superclass, ondelete="SET NULL")
            cls.generate_column_(
                wrtmodels, cls.superclass.model_name(), fk)
        
        if cls.subclass is not None: # table inheritance pg??
            fk = cls.build_fk_(
                cls.subclass, ondelete="CASCADE")
            cls.generate_column_(
                wrtmodels, cls.subclass.model_name(), fk)
        
        for spec in cls.member_data_items_:
            sa_name = cls.clean_name(spec.get_name())
            sa_attrs = columns[sa_name]

            clean_data_type = sa_attrs['clean_data_type']
            data_type = sa_attrs['data_type']

            if data_type in Simple_type_table:

                if sa_attrs['sa_type'] in sorted_type_table:
                    table, alias, parser = sorted_type_table[sa_attrs['sa_type']]

                    cls.generate_column_(
                        wrtmodels, sa_name, 'sa.types.%s' % (
                            alias or sa_attrs['sa_type']), 
                        **sa_attrs['options'])

                else:
                    sys.stderr.write('Unhandled simple type: %s %s\n' % (
                        sa_name, data_type, ))
            else:
                typeCls = getattr(cls.supermod_, clean_data_type, None)
                
                maxOccurs = sa_attrs.get('maxOccurs')
                if maxOccurs > 1: #manytomany
                    secondary = ('%s_%s_%s' % (
                        model_name, sa_name, typeCls.model_name(), ))
                    wrtmodels(
                        '    %s = sa.orm.relation(\n        "%s",\n' % (
                            sa_name, typeCls.model_name(full=True), )
                    )
                    wrtmodels(
                        '        secondary=%s_table)\n' % (secondary, )
                    )
                    cls.generate_secondary_(
                        wrtsecondary, secondary, cls, typeCls)
                elif maxOccurs == 1: #manytoone
                    minOccurs = sa_attrs.get('minOccurs')
                    
                    fk = cls.build_fk_(
                        typeCls,
                        ondelete="SET NULL" if (minOccurs < 1) else "CASCADE",
                    )
                    cls.generate_column_(
                        wrtmodels, sa_name, fk, 
                        nullable=(minOccurs < 1),
                    )
        
        pk_ = cls.pk()
        if cls.fields_idx and pk_ and pk_ not in cls.fields_idx:
            cls.generate_column_(
                wrtmodels, pk_, 'sa.types.Integer', 
                autoincrement=True)
        
        wrtmodels('\n')
        wrtmodels('    def __unicode__(self):\n')
        wrtmodels('        return u"%%s<%%s>" %% (self.__name__, self.%s)' 
            % pk_)
        wrtmodels('\n')


#
# Local functions

def find_attr_value_(node, attr_name=None):
    attrs = dict()
    if hasattr(node, 'attrib'): #lxml
        attrs = node.attrib or {}
    elif hasattr(node, 'attributes'): #minidom
        attrs = node.attributes or {}
    if attr_name is None:
        return attrs
    
    attr_parts = attr_name.split(':')
    value = None
    if len(attr_parts) == 1:
        value = attrs.get(attr_name)
    elif len(attr_parts) == 2:
        prefix, name = attr_parts
        namespace = node.nsmap.get(prefix)
        if namespace is not None:
            value = attrs.get('{%s}%s' % (namespace, name, ))
    if hasattr(value, 'value'): #minidom
        value = value.value
    return value

def make_unique_name_map(name_list):
    """Make a mapping from names to names that are unique ignoring case."""
    unique_name_table = {}
    unique_name_set = set()
    for name in name_list:
        make_unique_name(name, unique_name_table, unique_name_set)
    return unique_name_table


def make_unique_name(name, unique_name_table, unique_name_set):
    """Create a name that is unique even when we ignore case."""
    new_name = name
    lower_name = new_name.lower()
    count = 0
    while lower_name in unique_name_set:
        count += 1
        new_name = '{}_{:d}'.format(name, count)
        lower_name = new_name.lower()
    unique_name_table[name] = new_name
    unique_name_set.add(lower_name)

def model_filter(supermod, xsd_file):
    ret = dict()
    for class_name in supermod.__all__:
        ret[class_name] = dict(
            sa_name=class_name,
            generate=True,
        )
    return ret

def init_(supermod_, modtypes_, options_, class_names_, unique_name_map_):

    global options
    options = options_
    
    supermod_.__sa_attrs__ = dict()

    for class_name, info in class_names_.items():
        if not hasattr(supermod_, class_name):
            continue
        if class_name in Simple_type_table:
            del Simple_type_table[class_name]
        supermod_.__sa_attrs__[class_name] = dict(
            model_name=info['sa_name'],
            info=info,
            table_name= '%s%s' % (
                options.table_prefix_, unique_name_map_.get(info['sa_name']), ),
        )

    # super classes initialization
    for class_name in class_names_:
        if hasattr(supermod_, class_name):
            cls = getattr(supermod_, class_name)
            cls.init_fields_(supermod_, modtypes_)
        else:
            sys.stderr.write('class %s not defined\n' % class_name)

def prepare_(supermod_, options_, __sa_attrs__):

    global options
    options = options_

    supermod_.__sa_attrs__ = __sa_attrs__
    for class_name in supermod_.__all__:
        if class_name in Simple_type_table:
            del Simple_type_table[class_name]
        cls = getattr(supermod_, class_name)
        if hasattr(cls, 'index_spec'):
            cls.supermod_ = supermod_
            cls.index_spec()
