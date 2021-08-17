
from __future__ import print_function
import sys
import re as re_
import base64
import datetime as datetime_
import decimal as decimal_
try:
    from lxml import etree as etree_
except ImportError:
    from xml.etree import ElementTree as etree_
from generateds_definedsimpletypes import Defined_simple_type_table

from generateDS import AnyTypeIdentifier, mapName, cleanupName

if sys.version_info.major == 2:
    BaseStrType_ = basestring
else:
    BaseStrType_ = str


#
# Globals

# This variable enables users (modules) that use this module to
# check to make sure that they have imported the correct version
# of generatedssuper.py.
Generate_DS_Super_Marker_ = None
ExternalEncoding = ''
CDATA_pattern_ = re_.compile(r"<!\[CDATA\[.*?\]\]>", re_.DOTALL)

# Tables of builtin types
Simple_type_table = {
    'string': 'String',
    'normalizedString': 'String',
    'token': 'String',
    'base64Binary': 'Text',
    'hexBinary': 'Text',
    'integer': 'Integer',
    'positiveInteger': 'Integer',
    'negativeInteger': 'Integer',
    'nonNegativeInteger': 'Integer',
    'nonPositiveInteger': 'Integer',
    'long': 'BigInteger',
    'unsignedLong': 'BigInteger',
    'int': 'Integer',
    'unsignedInt': 'Integer',
    'short': 'SmallInteger',
    'unsignedShort': 'Integer',
    'byte': 'SmallInteger',
    'unsignedByte': 'Integer',
    'decimal': 'Numeric',
    'float': 'Float',
    'double': 'Float',
    'boolean': 'Boolean',
    'duration': 'Float',
    'dateTime': 'DateTime',
    'date': 'Date',
    'time': 'Time',
    'gYear': 'Integer',
    'gYearMonth': 'Integer',
    'gMonth': 'Integer',
    'gMonthDay': 'Integer',
    'gDay': 'Integer',
    'Name': 'String',
    'QName': 'String',
    'NCName': 'String',
    'anyURI': 'String',
    'language': 'String',
    'ID': 'String',
    'IDREF': 'String',
    'IDREFS': 'String',
    'ENTITY': 'String',
    'ENTITIES': 'String',
    'NOTATION': 'String',
    'NMTOKEN': 'String',
    'NMTOKENS': 'String',
}
Integer_type_table = {
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
}
Float_type_table = {
    'decimal': None,
    'float': None,
    'double': None,
}
String_type_table = {
    'string': None,
    'normalizedString': None,
    'token': None,
    'NCName': None,
    'ID': None,
    'IDREF': None,
    'IDREFS': None,
    'ENTITY': None,
    'ENTITIES': None,
    'NOTATION': None,
    'NMTOKEN': None,
    'NMTOKENS': None,
    'QName': None,
    'anyURI': None,
    'base64Binary': None,
    'hexBinary': None,
    'duration': None,
    'Name': None,
    'language': None,
}
Date_type_table = {
    'date': None,
    'gYear': None,
    'gYearMonth': None,
    'gMonth': None,
    'gMonthDay': None,
    'gDay': None,
}
DateTime_type_table = {
    'dateTime': None,
}
Time_type_table = {
    'time': None,
}
Boolean_type_table = {
    'boolean': None,
}


#
# Classes

class MdlWriter:
    def __init__(self):
        self.table_content = ''
        self.class_content = ''

    def wrt_table(self, content):
        self.table_content += content

    def wrt_class(self, content):
        self.class_content += content

    def wrt_table_nl(self, content):
        self.table_content += content + '\n'

    def wrt_class_nl(self, content):
        self.class_content += content + '\n'


class GeneratedsSuper(object):
#    def gds_format_string(self, input_data, input_name=''):
#        return input_data
#
#    def gds_format_integer(self, input_data, input_name=''):
#        return '%d' % input_data
#
#    def gds_format_float(self, input_data, input_name=''):
#        return '%f' % input_data
#
#    def gds_format_double(self, input_data, input_name=''):
#        return '%e' % input_data
#
#    def gds_format_boolean(self, input_data, input_name=''):
#        return '%s' % input_data
#
#    def gds_str_lower(self, instring):
#        return instring.lower()

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
    def generate_sa_model_(
            cls, wrtmodels, unique_name_map, class_suffixes):
        mdlwriter = MdlWriter()
        wrttn = mdlwriter.wrt_table_nl
        wrtcn = mdlwriter.wrt_class_nl
        if class_suffixes:
            model_suffix = '_model'
        else:
            model_suffix = ''
        class_name = unique_name_map.get(cls.__name__)
        wrtcn('\nclass %s%s(Base):\n' % (class_name, model_suffix, ))
        wrtcn('    __tablename__ = "%s"\n' % (class_name, ))
        wrtcn('    id = Column(Integer, primary_key=True, '
              'autoincrement=True)\n')
        if cls.superclass is not None:
            wrtcn('    %s_id = Column(Integer, '
                  'ForeignKey("%s%s.id"))' % (
                      cls.superclass.__name__,
                      cls.superclass.__name__, ''))
        for spec in cls.member_data_items_:
            name = spec.get_name()
            prefix, name = cls.get_prefix_name(name)
            data_type = spec.get_data_type()
            is_optional = spec.get_optional()
            prefix, data_type = cls.get_prefix_name(data_type)
            if data_type in Defined_simple_type_table:
                data_type = Defined_simple_type_table[data_type]
                prefix, data_type = cls.get_prefix_name(data_type.type_name)
            name = mapName(cleanupName(name))
            if name == 'id':
                name += 'x'
            elif name.endswith('_') and not name == AnyTypeIdentifier:
                name += 'x'
            clean_data_type = mapName(cleanupName(data_type))
            if data_type == AnyTypeIdentifier:
                data_type = 'string'
            if data_type in Simple_type_table:
                if is_optional:
                    options = 'nullable=True, '
                else:
                    options = ''
                if data_type in Integer_type_table:
                    if spec.container:
                        wrtcn('    %s = Column(String(1000), %s)' % (
                            name, options, ))
                    else:
                        wrtcn('    %s = Column(Integer, %s)' % (
                            name, options, ))
                elif data_type in Float_type_table:
                    if spec.container:
                        wrtcn('    %s = Column(String(1000), %s)' % (
                            name, options, ))
                    else:
                        wrtcn('    %s = Column(Float, %s)' % (
                            name, options, ))
                elif data_type in Date_type_table:
                    #wrtcn('    %s = Column(Date, %s)' % (
                    wrtcn('    %s = Column(String(32), %s)' % (
                        name, options, ))
                elif data_type in DateTime_type_table:
                    #wrtcn('    %s = Column(DateTime, %s)' % (
                    wrtcn('    %s = Column(String(32), %s)' % (
                        name, options, ))
                elif data_type in Time_type_table:
                    #wrtcn('    %s = Column(Time, %s)' % (
                    wrtcn('    %s = Column(String(32), %s)' % (
                        name, options, ))
                elif data_type in Boolean_type_table:
                    wrtcn('    %s = Column(Boolean, %s)' % (
                        name, options, ))
                elif data_type in String_type_table:
                    wrtcn(
                        '    %s = Column(String(1000), %s)' % (
                            name, options, ))
                else:
                    sys.stderr.write('Unhandled simple type: %s %s\n' % (
                        name, data_type, ))
            else:
                mapped_type = unique_name_map.get(clean_data_type)
                clean_data_type = class_name
                child_data_type = mapped_type
                child_name = name
                #
                # Generate Table for relationships to complex types if
                # it is a container, i.e. maxOccurs > 1.
                if True:
                    wrttn("%s_%s_%s_table = Table(" % (
                          clean_data_type, child_data_type, name, ))
                    wrttn("    '%s_%s_%s'," % (
                          clean_data_type, child_data_type, name, ))
                    wrttn("    Base.metadata,")
                    wrttn("    Column('%s_id', ForeignKey('%s.id'))," % (
                          clean_data_type, clean_data_type, ))
                    wrttn("    Column('%s_id', ForeignKey('%s.id'))," % (
                          child_data_type, child_data_type, ))
                    wrttn(")")
                    wrttn("")
                #
                # Generate the field in the class for relatinships to
                # complex types.
                wrtcn("    %s = relationship(" % (name, ))
                wrtcn("        '%s_model'," % (child_data_type, ))
                wrtcn("        secondary=%s_%s_%s_table," % (
                      clean_data_type, child_data_type, child_name))
                if not spec.container:
                    wrtcn("        uselist=False,")
                wrtcn("    )")
        wrtcn("")
        wrtcn("    def __repr__(self):")
        wrtcn("        return '<%s id: %%s>' %% (self.id, )" % (class_name, ))
        wrtcn("")
        wrtmodels(mdlwriter.table_content)
        wrtmodels(mdlwriter.class_content)

#class GeneratedsSuper(object):
    __hash__ = object.__hash__
    tzoff_pattern = re_.compile(r'(\+|-)((0\d|1[0-3]):[0-5]\d|14:00)$')
    class _FixedOffsetTZ(datetime_.tzinfo):
        def __init__(self, offset, name):
            self.__offset = datetime_.timedelta(minutes=offset)
            self.__name = name
        def utcoffset(self, dt):
            return self.__offset
        def tzname(self, dt):
            return self.__name
        def dst(self, dt):
            return None
    def gds_format_string(self, input_data, input_name=''):
        return input_data
    def gds_parse_string(self, input_data, node=None, input_name=''):
        return input_data
    def gds_validate_string(self, input_data, node=None, input_name=''):
        if not input_data:
            return ''
        else:
            return input_data
    def gds_format_base64(self, input_data, input_name=''):
        return base64.b64encode(input_data)
    def gds_validate_base64(self, input_data, node=None, input_name=''):
        return input_data
    def gds_format_integer(self, input_data, input_name=''):
        return '%d' % input_data
    def gds_parse_integer(self, input_data, node=None, input_name=''):
        try:
            ival = int(input_data)
        except (TypeError, ValueError) as exp:
            raise_parse_error(node, 'requires integer: %s' % exp)
        return ival
    def gds_validate_integer(self, input_data, node=None, input_name=''):
        return input_data
    def gds_format_integer_list(self, input_data, input_name=''):
        return '%s' % ' '.join(input_data)
    def gds_validate_integer_list(
            self, input_data, node=None, input_name=''):
        values = input_data.split()
        for value in values:
            try:
                int(value)
            except (TypeError, ValueError):
                raise_parse_error(node, 'Requires sequence of integers')
        return values
    def gds_format_float(self, input_data, input_name=''):
        return ('%.15f' % input_data).rstrip('0')
    def gds_parse_float(self, input_data, node=None, input_name=''):
        try:
            fval_ = float(input_data)
        except (TypeError, ValueError) as exp:
            raise_parse_error(node, 'requires float or double: %s' % exp)
        return fval_
    def gds_validate_float(self, input_data, node=None, input_name=''):
        try:
            value = float(input_data)
        except (TypeError, ValueError):
            raise_parse_error(node, 'Requires sequence of floats')
        return value
    def gds_format_float_list(self, input_data, input_name=''):
        return '%s' % ' '.join(input_data)
    def gds_validate_float_list(
            self, input_data, node=None, input_name=''):
        values = input_data.split()
        for value in values:
            try:
                float(value)
            except (TypeError, ValueError):
                raise_parse_error(node, 'Requires sequence of floats')
        return values
    def gds_format_decimal(self, input_data, input_name=''):
        return ('%0.10f' % input_data).rstrip('0')
    def gds_parse_decimal(self, input_data, node=None, input_name=''):
        try:
            decimal_value = decimal_.Decimal(input_data)
        except (TypeError, ValueError):
            raise_parse_error(node, 'Requires decimal value')
        return decimal_value
    def gds_validate_decimal(self, input_data, node=None, input_name=''):
        try:
            value = decimal_.Decimal(input_data)
        except (TypeError, ValueError):
            raise_parse_error(node, 'Requires decimal value')
        return value
    def gds_format_decimal_list(self, input_data, input_name=''):
        return '%s' % ' '.join(input_data)
    def gds_validate_decimal_list(
            self, input_data, node=None, input_name=''):
        values = input_data.split()
        for value in values:
            try:
                decimal_.Decimal(value)
            except (TypeError, ValueError):
                raise_parse_error(node, 'Requires sequence of decimal values')
        return values
    def gds_format_double(self, input_data, input_name=''):
        return '%e' % input_data
    def gds_parse_double(self, input_data, node=None, input_name=''):
        try:
            fval_ = float(input_data)
        except (TypeError, ValueError) as exp:
            raise_parse_error(node, 'requires float or double: %s' % exp)
        return fval_
    def gds_validate_double(self, input_data, node=None, input_name=''):
        return input_data
    def gds_format_double_list(self, input_data, input_name=''):
        return '%s' % ' '.join(input_data)
    def gds_validate_double_list(
            self, input_data, node=None, input_name=''):
        values = input_data.split()
        for value in values:
            try:
                float(value)
            except (TypeError, ValueError):
                raise_parse_error(node, 'Requires sequence of doubles')
        return values
    def gds_format_boolean(self, input_data, input_name=''):
        return ('%s' % input_data).lower()
    def gds_parse_boolean(self, input_data, node=None, input_name=''):
        if input_data in ('true', '1'):
            bval = True
        elif input_data in ('false', '0'):
            bval = False
        else:
            raise_parse_error(node, 'requires boolean')
        return bval
    def gds_validate_boolean(self, input_data, node=None, input_name=''):
        return input_data
    def gds_format_boolean_list(self, input_data, input_name=''):
        return '%s' % ' '.join(input_data)
    def gds_validate_boolean_list(
            self, input_data, node=None, input_name=''):
        values = input_data.split()
        for value in values:
            if value not in ('true', '1', 'false', '0', ):
                raise_parse_error(
                    node,
                    'Requires sequence of booleans '
                    '("true", "1", "false", "0")')
        return values
    def gds_validate_datetime(self, input_data, node=None, input_name=''):
        return input_data
    def gds_format_datetime(self, input_data, input_name=''):
        if input_data.microsecond == 0:
            _svalue = '%04d-%02d-%02dT%02d:%02d:%02d' % (
                input_data.year,
                input_data.month,
                input_data.day,
                input_data.hour,
                input_data.minute,
                input_data.second,
            )
        else:
            _svalue = '%04d-%02d-%02dT%02d:%02d:%02d.%s' % (
                input_data.year,
                input_data.month,
                input_data.day,
                input_data.hour,
                input_data.minute,
                input_data.second,
                ('%f' % (float(input_data.microsecond) / 1000000))[2:],
            )
        if input_data.tzinfo is not None:
            tzoff = input_data.tzinfo.utcoffset(input_data)
            if tzoff is not None:
                total_seconds = tzoff.seconds + (86400 * tzoff.days)
                if total_seconds == 0:
                    _svalue += 'Z'
                else:
                    if total_seconds < 0:
                        _svalue += '-'
                        total_seconds *= -1
                    else:
                        _svalue += '+'
                    hours = total_seconds // 3600
                    minutes = (total_seconds - (hours * 3600)) // 60
                    _svalue += '{0:02d}:{1:02d}'.format(hours, minutes)
        return _svalue
    @classmethod
    def gds_parse_datetime(cls, input_data):
        tz = None
        if input_data[-1] == 'Z':
            tz = GeneratedsSuper._FixedOffsetTZ(0, 'UTC')
            input_data = input_data[:-1]
        else:
            results = GeneratedsSuper.tzoff_pattern.search(input_data)
            if results is not None:
                tzoff_parts = results.group(2).split(':')
                tzoff = int(tzoff_parts[0]) * 60 + int(tzoff_parts[1])
                if results.group(1) == '-':
                    tzoff *= -1
                tz = GeneratedsSuper._FixedOffsetTZ(
                    tzoff, results.group(0))
                input_data = input_data[:-6]
        time_parts = input_data.split('.')
        if len(time_parts) > 1:
            micro_seconds = int(float('0.' + time_parts[1]) * 1000000)
            input_data = '%s.%s' % (
                time_parts[0], "{}".format(micro_seconds).rjust(6, "0"), )
            dt = datetime_.datetime.strptime(
                input_data, '%Y-%m-%dT%H:%M:%S.%f')
        else:
            dt = datetime_.datetime.strptime(
                input_data, '%Y-%m-%dT%H:%M:%S')
        dt = dt.replace(tzinfo=tz)
        return dt
    def gds_validate_date(self, input_data, node=None, input_name=''):
        return input_data
    def gds_format_date(self, input_data, input_name=''):
        _svalue = '%04d-%02d-%02d' % (
            input_data.year,
            input_data.month,
            input_data.day,
        )
        try:
            if input_data.tzinfo is not None:
                tzoff = input_data.tzinfo.utcoffset(input_data)
                if tzoff is not None:
                    total_seconds = tzoff.seconds + (86400 * tzoff.days)
                    if total_seconds == 0:
                        _svalue += 'Z'
                    else:
                        if total_seconds < 0:
                            _svalue += '-'
                            total_seconds *= -1
                        else:
                            _svalue += '+'
                        hours = total_seconds // 3600
                        minutes = (total_seconds - (hours * 3600)) // 60
                        _svalue += '{0:02d}:{1:02d}'.format(
                            hours, minutes)
        except AttributeError:
            pass
        return _svalue
    @classmethod
    def gds_parse_date(cls, input_data):
        tz = None
        if input_data[-1] == 'Z':
            tz = GeneratedsSuper._FixedOffsetTZ(0, 'UTC')
            input_data = input_data[:-1]
        else:
            results = GeneratedsSuper.tzoff_pattern.search(input_data)
            if results is not None:
                tzoff_parts = results.group(2).split(':')
                tzoff = int(tzoff_parts[0]) * 60 + int(tzoff_parts[1])
                if results.group(1) == '-':
                    tzoff *= -1
                tz = GeneratedsSuper._FixedOffsetTZ(
                    tzoff, results.group(0))
                input_data = input_data[:-6]
        dt = datetime_.datetime.strptime(input_data, '%Y-%m-%d')
        dt = dt.replace(tzinfo=tz)
        return dt.date()
    def gds_validate_time(self, input_data, node=None, input_name=''):
        return input_data
    def gds_format_time(self, input_data, input_name=''):
        if input_data.microsecond == 0:
            _svalue = '%02d:%02d:%02d' % (
                input_data.hour,
                input_data.minute,
                input_data.second,
            )
        else:
            _svalue = '%02d:%02d:%02d.%s' % (
                input_data.hour,
                input_data.minute,
                input_data.second,
                ('%f' % (float(input_data.microsecond) / 1000000))[2:],
            )
        if input_data.tzinfo is not None:
            tzoff = input_data.tzinfo.utcoffset(input_data)
            if tzoff is not None:
                total_seconds = tzoff.seconds + (86400 * tzoff.days)
                if total_seconds == 0:
                    _svalue += 'Z'
                else:
                    if total_seconds < 0:
                        _svalue += '-'
                        total_seconds *= -1
                    else:
                        _svalue += '+'
                    hours = total_seconds // 3600
                    minutes = (total_seconds - (hours * 3600)) // 60
                    _svalue += '{0:02d}:{1:02d}'.format(hours, minutes)
        return _svalue
    def gds_validate_simple_patterns(self, patterns, target):
        # pat is a list of lists of strings/patterns.
        # The target value must match at least one of the patterns
        # in order for the test to succeed.
        found1 = True
        for patterns1 in patterns:
            found2 = False
            for patterns2 in patterns1:
                mo = re_.search(patterns2, target)
                if mo is not None and len(mo.group(0)) == len(target):
                    found2 = True
                    break
            if not found2:
                found1 = False
                break
        return found1
    @classmethod
    def gds_parse_time(cls, input_data):
        tz = None
        if input_data[-1] == 'Z':
            tz = GeneratedsSuper._FixedOffsetTZ(0, 'UTC')
            input_data = input_data[:-1]
        else:
            results = GeneratedsSuper.tzoff_pattern.search(input_data)
            if results is not None:
                tzoff_parts = results.group(2).split(':')
                tzoff = int(tzoff_parts[0]) * 60 + int(tzoff_parts[1])
                if results.group(1) == '-':
                    tzoff *= -1
                tz = GeneratedsSuper._FixedOffsetTZ(
                    tzoff, results.group(0))
                input_data = input_data[:-6]
        if len(input_data.split('.')) > 1:
            dt = datetime_.datetime.strptime(input_data, '%H:%M:%S.%f')
        else:
            dt = datetime_.datetime.strptime(input_data, '%H:%M:%S')
        dt = dt.replace(tzinfo=tz)
        return dt.time()
    def gds_str_lower(self, instring):
        return instring.lower()
    def get_path_(self, node):
        path_list = []
        self.get_path_list_(node, path_list)
        path_list.reverse()
        path = '/'.join(path_list)
        return path
    Tag_strip_pattern_ = re_.compile(r'\{.*\}')
    def get_path_list_(self, node, path_list):
        if node is None:
            return
        tag = GeneratedsSuper.Tag_strip_pattern_.sub('', node.tag)
        if tag:
            path_list.append(tag)
        self.get_path_list_(node.getparent(), path_list)
    def get_class_obj_(self, node, default_class=None):
        class_obj1 = default_class
        if 'xsi' in node.nsmap:
            classname = node.get('{%s}type' % node.nsmap['xsi'])
            if classname is not None:
                names = classname.split(':')
                if len(names) == 2:
                    classname = names[1]
                class_obj2 = globals().get(classname)
                if class_obj2 is not None:
                    class_obj1 = class_obj2
        return class_obj1
    def gds_build_any(self, node, type_name=None):
        # provide default value in case option --disable-xml is used.
        content = ""
        content = etree_.tostring(node, encoding="unicode")
        return content
    @classmethod
    def gds_reverse_node_mapping(cls, mapping):
        return dict(((v, k) for k, v in mapping.items()))
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
    @staticmethod
    def convert_unicode(instring):
        if isinstance(instring, str):
            result = quote_xml(instring)
        elif sys.version_info.major == 2 and isinstance(instring, unicode):
            result = quote_xml(instring).encode('utf8')
        else:
            result = GeneratedsSuper.gds_encode(str(instring))
        return result
    def __eq__(self, other):
        def excl_select_objs_(obj):
            return (obj[0] != 'parent_object_' and
                    obj[0] != 'gds_collector_')
        if type(self) != type(other):
            return False
        return list(
            filter(excl_select_objs_, self.__dict__.items())
        ) == list(
            filter(excl_select_objs_, other.__dict__.items()))
    def __ne__(self, other):
        return not self.__eq__(other)
    # Django ETL transform hooks.
    def gds_djo_etl_transform(self):
        pass
    def gds_djo_etl_transform_db_obj(self, dbobj):
        pass
    # SQLAlchemy ETL transform hooks.
    def gds_sqa_etl_transform(self):
        return 0, None
    def gds_sqa_etl_transform_db_obj(self, dbobj):
        pass
    def gds_get_node_lineno_(self):
        if (hasattr(self, "gds_elementtree_node_") and
                self.gds_elementtree_node_ is not None):
            return ' near line {}'.format(
                self.gds_elementtree_node_.sourceline)
        else:
            return ""

class GDSParseError(Exception):
    pass


def raise_parse_error(node, msg):
    if node is not None:
        msg = '%s (element %s/line %d)' % (msg, node.tag, node.sourceline, )
    raise GDSParseError(msg)


def quote_xml(inStr):
    "Escape markup chars, but do not modify CDATA sections."
    if not inStr:
        return ''
    s1 = (isinstance(inStr, BaseStrType_) and inStr or '%s' % inStr)
    s2 = ''
    pos = 0
    matchobjects = CDATA_pattern_.finditer(s1)
    for mo in matchobjects:
        s3 = s1[pos:mo.start()]
        s2 += quote_xml_aux(s3)
        s2 += s1[mo.start():mo.end()]
        pos = mo.end()
    s3 = s1[pos:]
    s2 += quote_xml_aux(s3)
    return s2


def quote_xml_aux(inStr):
    s1 = inStr.replace('&', '&amp;')
    s1 = s1.replace('<', '&lt;')
    s1 = s1.replace('>', '&gt;')
    return s1
