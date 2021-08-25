#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# Generated  by generateDS.py.
# Python 3.8.11 (default, Aug  3 2021, 15:09:35)  [GCC 7.5.0]
#
# Command line options:
#   ('--no-dates', '')
#   ('--no-versions', '')
#   ('--silence', '')
#   ('--member-specs', 'list')
#   ('-f', '')
#   ('-o', 'tests/to_etree2_sup.py')
#   ('-s', 'tests/to_etree2_sub.py')
#   ('--export', 'etree')
#   ('--silence', '')
#   ('--super', 'to_etree2_sup')
#
# Command line arguments:
#   tests/to_etree.xsd
#
# Command line:
#   generateDS.py --no-dates --no-versions --silence --member-specs="list" -f -o "tests/to_etree2_sup.py" -s "tests/to_etree2_sub.py" --export="etree" --silence --super="to_etree2_sup" tests/to_etree.xsd
#
# Current working directory (os.getcwd()):
#   generateds
#

import sys
try:
    ModulenotfoundExp_ = ModuleNotFoundError
except NameError:
    ModulenotfoundExp_ = ImportError
from six.moves import zip_longest
import os
import re as re_
import base64
import datetime as datetime_
import decimal as decimal_
from lxml import etree as etree_


Validate_simpletypes_ = True
SaveElementTreeNode = True
if sys.version_info.major == 2:
    BaseStrType_ = basestring
else:
    BaseStrType_ = str


def parsexml_(infile, parser=None, **kwargs):
    if parser is None:
        # Use the lxml ElementTree compatible parser so that, e.g.,
        #   we ignore comments.
        try:
            parser = etree_.ETCompatXMLParser()
        except AttributeError:
            # fallback to xml.etree
            parser = etree_.XMLParser()
    try:
        if isinstance(infile, os.PathLike):
            infile = os.path.join(infile)
    except AttributeError:
        pass
    doc = etree_.parse(infile, parser=parser, **kwargs)
    return doc

def parsexmlstring_(instring, parser=None, **kwargs):
    if parser is None:
        # Use the lxml ElementTree compatible parser so that, e.g.,
        #   we ignore comments.
        try:
            parser = etree_.ETCompatXMLParser()
        except AttributeError:
            # fallback to xml.etree
            parser = etree_.XMLParser()
    element = etree_.fromstring(instring, parser=parser, **kwargs)
    return element

#
# Namespace prefix definition table (and other attributes, too)
#
# The module generatedsnamespaces, if it is importable, must contain
# a dictionary named GeneratedsNamespaceDefs.  This Python dictionary
# should map element type names (strings) to XML schema namespace prefix
# definitions.  The export method for any class for which there is
# a namespace prefix definition, will export that definition in the
# XML representation of that element.  See the export method of
# any generated element type class for an example of the use of this
# table.
# A sample table is:
#
#     # File: generatedsnamespaces.py
#
#     GenerateDSNamespaceDefs = {
#         "ElementtypeA": "http://www.xxx.com/namespaceA",
#         "ElementtypeB": "http://www.xxx.com/namespaceB",
#     }
#
# Additionally, the generatedsnamespaces module can contain a python
# dictionary named GenerateDSNamespaceTypePrefixes that associates element
# types with the namespace prefixes that are to be added to the
# "xsi:type" attribute value.  See the _exportAttributes method of
# any generated element type and the generation of "xsi:type" for an
# example of the use of this table.
# An example table:
#
#     # File: generatedsnamespaces.py
#
#     GenerateDSNamespaceTypePrefixes = {
#         "ElementtypeC": "aaa:",
#         "ElementtypeD": "bbb:",
#     }
#

try:
    from generatedsnamespaces import GenerateDSNamespaceDefs as GenerateDSNamespaceDefs_
except ModulenotfoundExp_ :
    GenerateDSNamespaceDefs_ = {}
try:
    from generatedsnamespaces import GenerateDSNamespaceTypePrefixes as GenerateDSNamespaceTypePrefixes_
except ModulenotfoundExp_ :
    GenerateDSNamespaceTypePrefixes_ = {}

#
# You can replace the following class definition by defining an
# importable module named "generatedscollector" containing a class
# named "GdsCollector".  See the default class definition below for
# clues about the possible content of that class.
#
try:
    from generatedscollector import GdsCollector as GdsCollector_
except ModulenotfoundExp_ :

    class GdsCollector_(object):

        def __init__(self, messages=None):
            if messages is None:
                self.messages = []
            else:
                self.messages = messages

        def add_message(self, msg):
            self.messages.append(msg)

        def get_messages(self):
            return self.messages

        def clear_messages(self):
            self.messages = []

        def print_messages(self):
            for msg in self.messages:
                print("Warning: {}".format(msg))

        def write_messages(self, outstream):
            for msg in self.messages:
                outstream.write("Warning: {}\n".format(msg))


#
# The super-class for enum types
#

try:
    from enum import Enum
except ModulenotfoundExp_ :
    Enum = object

#
# The root super-class for element type classes
#
# Calls to the methods in these classes are generated by generateDS.py.
# You can replace these methods by re-implementing the following class
#   in a module named generatedssuper.py.

try:
    from generatedssuper import GeneratedsSuper
except ModulenotfoundExp_ as exp:
    try:
        from generatedssupersuper import GeneratedsSuperSuper
    except ModulenotfoundExp_ as exp:
        class GeneratedsSuperSuper(object):
            pass
    
    class GeneratedsSuper(GeneratedsSuperSuper):
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
                raise_parse_error(node, 'Requires integer value: %s' % exp)
            return ival
        def gds_validate_integer(self, input_data, node=None, input_name=''):
            try:
                value = int(input_data)
            except (TypeError, ValueError):
                raise_parse_error(node, 'Requires integer value')
            return value
        def gds_format_integer_list(self, input_data, input_name=''):
            if len(input_data) > 0 and not isinstance(input_data[0], BaseStrType_):
                input_data = [str(s) for s in input_data]
            return '%s' % ' '.join(input_data)
        def gds_validate_integer_list(
                self, input_data, node=None, input_name=''):
            values = input_data.split()
            for value in values:
                try:
                    int(value)
                except (TypeError, ValueError):
                    raise_parse_error(node, 'Requires sequence of integer values')
            return values
        def gds_format_float(self, input_data, input_name=''):
            return ('%.15f' % input_data).rstrip('0')
        def gds_parse_float(self, input_data, node=None, input_name=''):
            try:
                fval_ = float(input_data)
            except (TypeError, ValueError) as exp:
                raise_parse_error(node, 'Requires float or double value: %s' % exp)
            return fval_
        def gds_validate_float(self, input_data, node=None, input_name=''):
            try:
                value = float(input_data)
            except (TypeError, ValueError):
                raise_parse_error(node, 'Requires float value')
            return value
        def gds_format_float_list(self, input_data, input_name=''):
            if len(input_data) > 0 and not isinstance(input_data[0], BaseStrType_):
                input_data = [str(s) for s in input_data]
            return '%s' % ' '.join(input_data)
        def gds_validate_float_list(
                self, input_data, node=None, input_name=''):
            values = input_data.split()
            for value in values:
                try:
                    float(value)
                except (TypeError, ValueError):
                    raise_parse_error(node, 'Requires sequence of float values')
            return values
        def gds_format_decimal(self, input_data, input_name=''):
            return_value = '%s' % input_data
            if '.' in return_value:
                return_value = return_value.rstrip('0')
                if return_value.endswith('.'):
                    return_value = return_value.rstrip('.')
            return return_value
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
            if len(input_data) > 0 and not isinstance(input_data[0], BaseStrType_):
                input_data = [str(s) for s in input_data]
            return ' '.join([self.gds_format_decimal(item) for item in input_data])
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
            return '%s' % input_data
        def gds_parse_double(self, input_data, node=None, input_name=''):
            try:
                fval_ = float(input_data)
            except (TypeError, ValueError) as exp:
                raise_parse_error(node, 'Requires double or float value: %s' % exp)
            return fval_
        def gds_validate_double(self, input_data, node=None, input_name=''):
            try:
                value = float(input_data)
            except (TypeError, ValueError):
                raise_parse_error(node, 'Requires double or float value')
            return value
        def gds_format_double_list(self, input_data, input_name=''):
            if len(input_data) > 0 and not isinstance(input_data[0], BaseStrType_):
                input_data = [str(s) for s in input_data]
            return '%s' % ' '.join(input_data)
        def gds_validate_double_list(
                self, input_data, node=None, input_name=''):
            values = input_data.split()
            for value in values:
                try:
                    float(value)
                except (TypeError, ValueError):
                    raise_parse_error(
                        node, 'Requires sequence of double or float values')
            return values
        def gds_format_boolean(self, input_data, input_name=''):
            return ('%s' % input_data).lower()
        def gds_parse_boolean(self, input_data, node=None, input_name=''):
            if input_data in ('true', '1'):
                bval = True
            elif input_data in ('false', '0'):
                bval = False
            else:
                raise_parse_error(node, 'Requires boolean value')
            return bval
        def gds_validate_boolean(self, input_data, node=None, input_name=''):
            if input_data not in (True, 1, False, 0, ):
                raise_parse_error(
                    node,
                    'Requires boolean value '
                    '(one of True, 1, False, 0)')
            return input_data
        def gds_format_boolean_list(self, input_data, input_name=''):
            if len(input_data) > 0 and not isinstance(input_data[0], BaseStrType_):
                input_data = [str(s) for s in input_data]
            return '%s' % ' '.join(input_data)
        def gds_validate_boolean_list(
                self, input_data, node=None, input_name=''):
            values = input_data.split()
            for value in values:
                value = self.gds_parse_boolean(value, node, input_name)
                if value not in (True, 1, False, 0, ):
                    raise_parse_error(
                        node,
                        'Requires sequence of boolean values '
                        '(one of True, 1, False, 0)')
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
        def gds_check_cardinality_(
                self, value, input_name,
                min_occurs=0, max_occurs=1, required=None):
            if value is None:
                length = 0
            elif isinstance(value, list):
                length = len(value)
            else:
                length = 1
            if required is not None :
                if required and length < 1:
                    self.gds_collector_.add_message(
                        "Required value {}{} is missing".format(
                            input_name, self.gds_get_node_lineno_()))
            if length < min_occurs:
                self.gds_collector_.add_message(
                    "Number of values for {}{} is below "
                    "the minimum allowed, "
                    "expected at least {}, found {}".format(
                        input_name, self.gds_get_node_lineno_(),
                        min_occurs, length))
            elif length > max_occurs:
                self.gds_collector_.add_message(
                    "Number of values for {}{} is above "
                    "the maximum allowed, "
                    "expected at most {}, found {}".format(
                        input_name, self.gds_get_node_lineno_(),
                        max_occurs, length))
        def gds_validate_builtin_ST_(
                self, validator, value, input_name,
                min_occurs=None, max_occurs=None, required=None):
            if value is not None:
                try:
                    validator(value, input_name=input_name)
                except GDSParseError as parse_error:
                    self.gds_collector_.add_message(str(parse_error))
        def gds_validate_defined_ST_(
                self, validator, value, input_name,
                min_occurs=None, max_occurs=None, required=None):
            if value is not None:
                try:
                    validator(value)
                except GDSParseError as parse_error:
                    self.gds_collector_.add_message(str(parse_error))
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
            return all(x == y for x, y in zip_longest(
                filter(excl_select_objs_, self.__dict__.items()),
                filter(excl_select_objs_, other.__dict__.items())))
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
    
    
    def getSubclassFromModule_(module, class_):
        '''Get the subclass of a class from a specific module.'''
        name = class_.__name__ + 'Sub'
        if hasattr(module, name):
            return getattr(module, name)
        else:
            return None


#
# If you have installed IPython you can uncomment and use the following.
# IPython is available from http://ipython.scipy.org/.
#

## from IPython.Shell import IPShellEmbed
## args = ''
## ipshell = IPShellEmbed(args,
##     banner = 'Dropping into IPython',
##     exit_msg = 'Leaving Interpreter, back to program.')

# Then use the following line where and when you want to drop into the
# IPython shell:
#    ipshell('<some message> -- Entering ipshell.\nHit Ctrl-D to exit')

#
# Globals
#

ExternalEncoding = ''
# Set this to false in order to deactivate during export, the use of
# name space prefixes captured from the input document.
UseCapturedNS_ = True
CapturedNsmap_ = {}
Tag_pattern_ = re_.compile(r'({.*})?(.*)')
String_cleanup_pat_ = re_.compile(r"[\n\r\s]+")
Namespace_extract_pat_ = re_.compile(r'{(.*)}(.*)')
CDATA_pattern_ = re_.compile(r"<!\[CDATA\[.*?\]\]>", re_.DOTALL)

# Change this to redirect the generated superclass module to use a
# specific subclass module.
CurrentSubclassModule_ = None

#
# Support/utility functions.
#


def showIndent(outfile, level, pretty_print=True):
    if pretty_print:
        for idx in range(level):
            outfile.write('    ')


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


def quote_attrib(inStr):
    s1 = (isinstance(inStr, BaseStrType_) and inStr or '%s' % inStr)
    s1 = s1.replace('&', '&amp;')
    s1 = s1.replace('<', '&lt;')
    s1 = s1.replace('>', '&gt;')
    if '"' in s1:
        if "'" in s1:
            s1 = '"%s"' % s1.replace('"', "&quot;")
        else:
            s1 = "'%s'" % s1
    else:
        s1 = '"%s"' % s1
    return s1


def quote_python(inStr):
    s1 = inStr
    if s1.find("'") == -1:
        if s1.find('\n') == -1:
            return "'%s'" % s1
        else:
            return "'''%s'''" % s1
    else:
        if s1.find('"') != -1:
            s1 = s1.replace('"', '\\"')
        if s1.find('\n') == -1:
            return '"%s"' % s1
        else:
            return '"""%s"""' % s1


def get_all_text_(node):
    if node.text is not None:
        text = node.text
    else:
        text = ''
    for child in node:
        if child.tail is not None:
            text += child.tail
    return text


def find_attr_value_(attr_name, node):
    attrs = node.attrib
    attr_parts = attr_name.split(':')
    value = None
    if len(attr_parts) == 1:
        value = attrs.get(attr_name)
    elif len(attr_parts) == 2:
        prefix, name = attr_parts
        if prefix == 'xml':
            namespace = 'http://www.w3.org/XML/1998/namespace'
        else:
            namespace = node.nsmap.get(prefix)
        if namespace is not None:
            value = attrs.get('{%s}%s' % (namespace, name, ))
    return value


def encode_str_2_3(instr):
    return instr


class GDSParseError(Exception):
    pass


def raise_parse_error(node, msg):
    if node is not None:
        msg = '%s (element %s/line %d)' % (msg, node.tag, node.sourceline, )
    raise GDSParseError(msg)


class MixedContainer:
    # Constants for category:
    CategoryNone = 0
    CategoryText = 1
    CategorySimple = 2
    CategoryComplex = 3
    # Constants for content_type:
    TypeNone = 0
    TypeText = 1
    TypeString = 2
    TypeInteger = 3
    TypeFloat = 4
    TypeDecimal = 5
    TypeDouble = 6
    TypeBoolean = 7
    TypeBase64 = 8
    def __init__(self, category, content_type, name, value):
        self.category = category
        self.content_type = content_type
        self.name = name
        self.value = value
    def getCategory(self):
        return self.category
    def getContenttype(self, content_type):
        return self.content_type
    def getValue(self):
        return self.value
    def getName(self):
        return self.name
    def export(self, outfile, level, name, namespace,
               pretty_print=True):
        if self.category == MixedContainer.CategoryText:
            # Prevent exporting empty content as empty lines.
            if self.value.strip():
                outfile.write(self.value)
        elif self.category == MixedContainer.CategorySimple:
            self.exportSimple(outfile, level, name)
        else:    # category == MixedContainer.CategoryComplex
            self.value.export(
                outfile, level, namespace, name_=name,
                pretty_print=pretty_print)
    def exportSimple(self, outfile, level, name):
        if self.content_type == MixedContainer.TypeString:
            outfile.write('<%s>%s</%s>' % (
                self.name, self.value, self.name))
        elif self.content_type == MixedContainer.TypeInteger or \
                self.content_type == MixedContainer.TypeBoolean:
            outfile.write('<%s>%d</%s>' % (
                self.name, self.value, self.name))
        elif self.content_type == MixedContainer.TypeFloat or \
                self.content_type == MixedContainer.TypeDecimal:
            outfile.write('<%s>%f</%s>' % (
                self.name, self.value, self.name))
        elif self.content_type == MixedContainer.TypeDouble:
            outfile.write('<%s>%g</%s>' % (
                self.name, self.value, self.name))
        elif self.content_type == MixedContainer.TypeBase64:
            outfile.write('<%s>%s</%s>' % (
                self.name,
                base64.b64encode(self.value),
                self.name))
    def to_etree(self, element, mapping_=None, reverse_mapping_=None, nsmap_=None):
        if self.category == MixedContainer.CategoryText:
            # Prevent exporting empty content as empty lines.
            if self.value.strip():
                if len(element) > 0:
                    if element[-1].tail is None:
                        element[-1].tail = self.value
                    else:
                        element[-1].tail += self.value
                else:
                    if element.text is None:
                        element.text = self.value
                    else:
                        element.text += self.value
        elif self.category == MixedContainer.CategorySimple:
            subelement = etree_.SubElement(
                element, '%s' % self.name)
            subelement.text = self.to_etree_simple()
        else:    # category == MixedContainer.CategoryComplex
            self.value.to_etree(element)
    def to_etree_simple(self, mapping_=None, reverse_mapping_=None, nsmap_=None):
        if self.content_type == MixedContainer.TypeString:
            text = self.value
        elif (self.content_type == MixedContainer.TypeInteger or
                self.content_type == MixedContainer.TypeBoolean):
            text = '%d' % self.value
        elif (self.content_type == MixedContainer.TypeFloat or
                self.content_type == MixedContainer.TypeDecimal):
            text = '%f' % self.value
        elif self.content_type == MixedContainer.TypeDouble:
            text = '%g' % self.value
        elif self.content_type == MixedContainer.TypeBase64:
            text = '%s' % base64.b64encode(self.value)
        return text
    def exportLiteral(self, outfile, level, name):
        if self.category == MixedContainer.CategoryText:
            showIndent(outfile, level)
            outfile.write(
                'model_.MixedContainer(%d, %d, "%s", "%s"),\n' % (
                    self.category, self.content_type,
                    self.name, self.value))
        elif self.category == MixedContainer.CategorySimple:
            showIndent(outfile, level)
            outfile.write(
                'model_.MixedContainer(%d, %d, "%s", "%s"),\n' % (
                    self.category, self.content_type,
                    self.name, self.value))
        else:    # category == MixedContainer.CategoryComplex
            showIndent(outfile, level)
            outfile.write(
                'model_.MixedContainer(%d, %d, "%s",\n' % (
                    self.category, self.content_type, self.name,))
            self.value.exportLiteral(outfile, level + 1)
            showIndent(outfile, level)
            outfile.write(')\n')


class MemberSpec_(object):
    def __init__(self, name='', data_type='', container=0,
            optional=0, child_attrs=None, choice=None):
        self.name = name
        self.data_type = data_type
        self.container = container
        self.child_attrs = child_attrs
        self.choice = choice
        self.optional = optional
    def set_name(self, name): self.name = name
    def get_name(self): return self.name
    def set_data_type(self, data_type): self.data_type = data_type
    def get_data_type_chain(self): return self.data_type
    def get_data_type(self):
        if isinstance(self.data_type, list):
            if len(self.data_type) > 0:
                return self.data_type[-1]
            else:
                return 'xs:string'
        else:
            return self.data_type
    def set_container(self, container): self.container = container
    def get_container(self): return self.container
    def set_child_attrs(self, child_attrs): self.child_attrs = child_attrs
    def get_child_attrs(self): return self.child_attrs
    def set_choice(self, choice): self.choice = choice
    def get_choice(self): return self.choice
    def set_optional(self, optional): self.optional = optional
    def get_optional(self): return self.optional


def _cast(typ, value):
    if typ is None or value is None:
        return value
    return typ(value)

#
# Data representation classes.
#


class ArrayTypes(str, Enum):
    FLOAT='float'
    INT='int'
    NAME='Name'
    TOKEN='token'


class peopleType(GeneratedsSuper):
    __hash__ = GeneratedsSuper.__hash__
    member_data_items_ = [
        MemberSpec_('comments', 'commentsType', 1, 0, {'maxOccurs': 'unbounded', 'name': 'comments', 'type': 'commentsType'}, None),
        MemberSpec_('person', 'personType', 1, 0, {'maxOccurs': 'unbounded', 'name': 'person', 'type': 'personType'}, None),
        MemberSpec_('specialperson', 'specialperson', 1, 0, {'maxOccurs': 'unbounded', 'name': 'specialperson', 'type': 'specialperson'}, None),
        MemberSpec_('programmer', 'programmerType', 1, 0, {'maxOccurs': 'unbounded', 'name': 'programmer', 'type': 'programmerType'}, None),
        MemberSpec_('python_programmer', 'python-programmerType', 1, 0, {'maxOccurs': 'unbounded', 'name': 'python-programmer', 'type': 'python-programmerType'}, None),
        MemberSpec_('java_programmer', 'java-programmerType', 1, 0, {'maxOccurs': 'unbounded', 'name': 'java-programmer', 'type': 'java-programmerType'}, None),
    ]
    subclass = None
    superclass = None
    def __init__(self, comments=None, person=None, specialperson=None, programmer=None, python_programmer=None, java_programmer=None, gds_collector_=None, **kwargs_):
        self.gds_collector_ = gds_collector_
        self.gds_elementtree_node_ = None
        self.original_tagname_ = None
        self.parent_object_ = kwargs_.get('parent_object_')
        self.ns_prefix_ = None
        if comments is None:
            self.comments = []
        else:
            self.comments = comments
        self.comments_nsprefix_ = None
        if person is None:
            self.person = []
        else:
            self.person = person
        self.person_nsprefix_ = None
        if specialperson is None:
            self.specialperson = []
        else:
            self.specialperson = specialperson
        self.specialperson_nsprefix_ = None
        if programmer is None:
            self.programmer = []
        else:
            self.programmer = programmer
        self.programmer_nsprefix_ = None
        if python_programmer is None:
            self.python_programmer = []
        else:
            self.python_programmer = python_programmer
        self.python_programmer_nsprefix_ = None
        if java_programmer is None:
            self.java_programmer = []
        else:
            self.java_programmer = java_programmer
        self.java_programmer_nsprefix_ = None
    def factory(*args_, **kwargs_):
        if CurrentSubclassModule_ is not None:
            subclass = getSubclassFromModule_(
                CurrentSubclassModule_, peopleType)
            if subclass is not None:
                return subclass(*args_, **kwargs_)
        if peopleType.subclass:
            return peopleType.subclass(*args_, **kwargs_)
        else:
            return peopleType(*args_, **kwargs_)
    factory = staticmethod(factory)
    def get_ns_prefix_(self):
        return self.ns_prefix_
    def set_ns_prefix_(self, ns_prefix):
        self.ns_prefix_ = ns_prefix
    def get_comments(self):
        return self.comments
    def set_comments(self, comments):
        self.comments = comments
    def add_comments(self, value):
        self.comments.append(value)
    def insert_comments_at(self, index, value):
        self.comments.insert(index, value)
    def replace_comments_at(self, index, value):
        self.comments[index] = value
    def get_person(self):
        return self.person
    def set_person(self, person):
        self.person = person
    def add_person(self, value):
        self.person.append(value)
    def insert_person_at(self, index, value):
        self.person.insert(index, value)
    def replace_person_at(self, index, value):
        self.person[index] = value
    def get_specialperson(self):
        return self.specialperson
    def set_specialperson(self, specialperson):
        self.specialperson = specialperson
    def add_specialperson(self, value):
        self.specialperson.append(value)
    def insert_specialperson_at(self, index, value):
        self.specialperson.insert(index, value)
    def replace_specialperson_at(self, index, value):
        self.specialperson[index] = value
    def get_programmer(self):
        return self.programmer
    def set_programmer(self, programmer):
        self.programmer = programmer
    def add_programmer(self, value):
        self.programmer.append(value)
    def insert_programmer_at(self, index, value):
        self.programmer.insert(index, value)
    def replace_programmer_at(self, index, value):
        self.programmer[index] = value
    def get_python_programmer(self):
        return self.python_programmer
    def set_python_programmer(self, python_programmer):
        self.python_programmer = python_programmer
    def add_python_programmer(self, value):
        self.python_programmer.append(value)
    def insert_python_programmer_at(self, index, value):
        self.python_programmer.insert(index, value)
    def replace_python_programmer_at(self, index, value):
        self.python_programmer[index] = value
    def get_java_programmer(self):
        return self.java_programmer
    def set_java_programmer(self, java_programmer):
        self.java_programmer = java_programmer
    def add_java_programmer(self, value):
        self.java_programmer.append(value)
    def insert_java_programmer_at(self, index, value):
        self.java_programmer.insert(index, value)
    def replace_java_programmer_at(self, index, value):
        self.java_programmer[index] = value
    def _hasContent(self):
        if (
            self.comments or
            self.person or
            self.specialperson or
            self.programmer or
            self.python_programmer or
            self.java_programmer
        ):
            return True
        else:
            return False
    def to_etree(self, parent_element=None, name_='peopleType', mapping_=None, reverse_mapping_=None, nsmap_=None):
        if parent_element is None:
            element = etree_.Element(name_, nsmap=nsmap_)
        else:
            element = etree_.SubElement(parent_element, name_, nsmap=nsmap_)
        for comments_ in self.comments:
            comments_.to_etree(element, name_='comments', mapping_=mapping_, reverse_mapping_=reverse_mapping_, nsmap_=nsmap_)
        for person_ in self.person:
            person_.to_etree(element, name_='person', mapping_=mapping_, reverse_mapping_=reverse_mapping_, nsmap_=nsmap_)
        for specialperson_ in self.specialperson:
            specialperson_.to_etree(element, name_='specialperson', mapping_=mapping_, reverse_mapping_=reverse_mapping_, nsmap_=nsmap_)
        for programmer_ in self.programmer:
            programmer_.to_etree(element, name_='programmer', mapping_=mapping_, reverse_mapping_=reverse_mapping_, nsmap_=nsmap_)
        for python_programmer_ in self.python_programmer:
            python_programmer_.to_etree(element, name_='python-programmer', mapping_=mapping_, reverse_mapping_=reverse_mapping_, nsmap_=nsmap_)
        for java_programmer_ in self.java_programmer:
            java_programmer_.to_etree(element, name_='java-programmer', mapping_=mapping_, reverse_mapping_=reverse_mapping_, nsmap_=nsmap_)
        if mapping_ is not None:
            mapping_[id(self)] = element
        if reverse_mapping_ is not None:
            reverse_mapping_[element] = self
        return element
    def build(self, node, gds_collector_=None):
        self.gds_collector_ = gds_collector_
        if SaveElementTreeNode:
            self.gds_elementtree_node_ = node
        already_processed = set()
        self.ns_prefix_ = node.prefix
        self._buildAttributes(node, node.attrib, already_processed)
        for child in node:
            nodeName_ = Tag_pattern_.match(child.tag).groups()[-1]
            self._buildChildren(child, node, nodeName_, gds_collector_=gds_collector_)
        return self
    def _buildAttributes(self, node, attrs, already_processed):
        pass
    def _buildChildren(self, child_, node, nodeName_, fromsubclass_=False, gds_collector_=None):
        if nodeName_ == 'comments':
            obj_ = commentsType.factory(parent_object_=self)
            obj_.build(child_, gds_collector_=gds_collector_)
            self.comments.append(obj_)
            obj_.original_tagname_ = 'comments'
        elif nodeName_ == 'person':
            class_obj_ = self.get_class_obj_(child_, personType)
            obj_ = class_obj_.factory(parent_object_=self)
            obj_.build(child_, gds_collector_=gds_collector_)
            self.person.append(obj_)
            obj_.original_tagname_ = 'person'
        elif nodeName_ == 'specialperson':
            obj_ = specialperson.factory(parent_object_=self)
            obj_.build(child_, gds_collector_=gds_collector_)
            self.specialperson.append(obj_)
            obj_.original_tagname_ = 'specialperson'
        elif nodeName_ == 'programmer':
            class_obj_ = self.get_class_obj_(child_, programmerType)
            obj_ = class_obj_.factory(parent_object_=self)
            obj_.build(child_, gds_collector_=gds_collector_)
            self.programmer.append(obj_)
            obj_.original_tagname_ = 'programmer'
        elif nodeName_ == 'python-programmer':
            obj_ = python_programmerType.factory(parent_object_=self)
            obj_.build(child_, gds_collector_=gds_collector_)
            self.python_programmer.append(obj_)
            obj_.original_tagname_ = 'python-programmer'
        elif nodeName_ == 'java-programmer':
            obj_ = java_programmerType.factory(parent_object_=self)
            obj_.build(child_, gds_collector_=gds_collector_)
            self.java_programmer.append(obj_)
            obj_.original_tagname_ = 'java-programmer'
# end class peopleType


class commentsType(GeneratedsSuper):
    __hash__ = GeneratedsSuper.__hash__
    member_data_items_ = [
        MemberSpec_('emp', 'xs:string', 1, 0, {'maxOccurs': 'unbounded', 'name': 'emp', 'type': 'xs:string'}, None),
        MemberSpec_('bold', 'xs:string', 1, 0, {'maxOccurs': 'unbounded', 'name': 'bold', 'type': 'xs:string'}, None),
        MemberSpec_('valueOf_', [], 0),
    ]
    subclass = None
    superclass = None
    def __init__(self, emp=None, bold=None, valueOf_=None, mixedclass_=None, content_=None, gds_collector_=None, **kwargs_):
        self.gds_collector_ = gds_collector_
        self.gds_elementtree_node_ = None
        self.original_tagname_ = None
        self.parent_object_ = kwargs_.get('parent_object_')
        self.ns_prefix_ = None
        if emp is None:
            self.emp = []
        else:
            self.emp = emp
        self.emp_nsprefix_ = None
        if bold is None:
            self.bold = []
        else:
            self.bold = bold
        self.bold_nsprefix_ = None
        self.valueOf_ = valueOf_
        if mixedclass_ is None:
            self.mixedclass_ = MixedContainer
        else:
            self.mixedclass_ = mixedclass_
        if content_ is None:
            self.content_ = []
        else:
            self.content_ = content_
        self.valueOf_ = valueOf_
    def factory(*args_, **kwargs_):
        if CurrentSubclassModule_ is not None:
            subclass = getSubclassFromModule_(
                CurrentSubclassModule_, commentsType)
            if subclass is not None:
                return subclass(*args_, **kwargs_)
        if commentsType.subclass:
            return commentsType.subclass(*args_, **kwargs_)
        else:
            return commentsType(*args_, **kwargs_)
    factory = staticmethod(factory)
    def get_ns_prefix_(self):
        return self.ns_prefix_
    def set_ns_prefix_(self, ns_prefix):
        self.ns_prefix_ = ns_prefix
    def get_emp(self):
        return self.emp
    def set_emp(self, emp):
        self.emp = emp
    def add_emp(self, value):
        self.emp.append(value)
    def insert_emp_at(self, index, value):
        self.emp.insert(index, value)
    def replace_emp_at(self, index, value):
        self.emp[index] = value
    def get_bold(self):
        return self.bold
    def set_bold(self, bold):
        self.bold = bold
    def add_bold(self, value):
        self.bold.append(value)
    def insert_bold_at(self, index, value):
        self.bold.insert(index, value)
    def replace_bold_at(self, index, value):
        self.bold[index] = value
    def get_valueOf_(self): return self.valueOf_
    def set_valueOf_(self, valueOf_): self.valueOf_ = valueOf_
    def _hasContent(self):
        if (
            self.emp or
            self.bold or
            (1 if type(self.valueOf_) in [int,float] else self.valueOf_) or
            self.content_
        ):
            return True
        else:
            return False
    def to_etree(self, parent_element=None, name_='commentsType', mapping_=None, reverse_mapping_=None, nsmap_=None):
        if parent_element is None:
            element = etree_.Element(name_, nsmap=nsmap_)
        else:
            element = etree_.SubElement(parent_element, name_, nsmap=nsmap_)
        for item_ in self.content_:
            item_.to_etree(element, mapping_=mapping_, reverse_mapping_=reverse_mapping_, nsmap_=nsmap_)
        if mapping_ is not None:
            mapping_[id(self)] = element
        if reverse_mapping_ is not None:
            reverse_mapping_[element] = self
        return element
    def build(self, node, gds_collector_=None):
        self.gds_collector_ = gds_collector_
        if SaveElementTreeNode:
            self.gds_elementtree_node_ = node
        already_processed = set()
        self.ns_prefix_ = node.prefix
        self._buildAttributes(node, node.attrib, already_processed)
        self.valueOf_ = get_all_text_(node)
        if node.text is not None:
            obj_ = self.mixedclass_(MixedContainer.CategoryText,
                MixedContainer.TypeNone, '', node.text)
            self.content_.append(obj_)
        for child in node:
            nodeName_ = Tag_pattern_.match(child.tag).groups()[-1]
            self._buildChildren(child, node, nodeName_, gds_collector_=gds_collector_)
        return self
    def _buildAttributes(self, node, attrs, already_processed):
        pass
    def _buildChildren(self, child_, node, nodeName_, fromsubclass_=False, gds_collector_=None):
        if nodeName_ == 'emp' and child_.text is not None:
            valuestr_ = child_.text
            valuestr_ = self.gds_parse_string(valuestr_, node, 'emp')
            valuestr_ = self.gds_validate_string(valuestr_, node, 'emp')
            obj_ = self.mixedclass_(MixedContainer.CategorySimple,
                MixedContainer.TypeString, 'emp', valuestr_)
            self.content_.append(obj_)
            self.emp_nsprefix_ = child_.prefix
        elif nodeName_ == 'bold' and child_.text is not None:
            valuestr_ = child_.text
            valuestr_ = self.gds_parse_string(valuestr_, node, 'bold')
            valuestr_ = self.gds_validate_string(valuestr_, node, 'bold')
            obj_ = self.mixedclass_(MixedContainer.CategorySimple,
                MixedContainer.TypeString, 'bold', valuestr_)
            self.content_.append(obj_)
            self.bold_nsprefix_ = child_.prefix
        if not fromsubclass_ and child_.tail is not None:
            obj_ = self.mixedclass_(MixedContainer.CategoryText,
                MixedContainer.TypeNone, '', child_.tail)
            self.content_.append(obj_)
# end class commentsType


class personType(GeneratedsSuper):
    __hash__ = GeneratedsSuper.__hash__
    member_data_items_ = [
        MemberSpec_('value', 'xs:string', 0, 1, {'use': 'optional', 'name': 'value'}),
        MemberSpec_('id', 'xs:integer', 0, 1, {'use': 'optional', 'name': 'id'}),
        MemberSpec_('ratio', 'xs:float', 0, 1, {'use': 'optional', 'name': 'ratio'}),
        MemberSpec_('fruit', 'xs:string', 0, 1, {'use': 'optional', 'name': 'fruit'}),
        MemberSpec_('vegetable', 'xs:string', 0, 1, {'use': 'optional', 'name': 'vegetable'}),
        MemberSpec_('name', 'xs:string', 0, 0, {'name': 'name', 'type': 'xs:string'}, None),
        MemberSpec_('interest', 'xs:string', 1, 0, {'maxOccurs': 'unbounded', 'name': 'interest', 'type': 'xs:string'}, None),
        MemberSpec_('category', 'xs:integer', 0, 0, {'name': 'category', 'type': 'xs:integer'}, None),
        MemberSpec_('hot_agent', 'hot.agent', 0, 0, {'name': 'hot.agent', 'type': 'hot.agent'}, None),
        MemberSpec_('agent', 'agentType', 1, 0, {'maxOccurs': 'unbounded', 'name': 'agent', 'type': 'agentType'}, None),
        MemberSpec_('promoter', 'boosterType', 1, 0, {'maxOccurs': 'unbounded', 'name': 'promoter', 'type': 'boosterType'}, None),
        MemberSpec_('description', 'xs:string', 0, 0, {'name': 'description', 'type': 'xs:string'}, None),
        MemberSpec_('range_', ['RangeType', 'xs:integer'], 0, 0, {'name': 'range', 'type': 'xs:integer'}, None),
    ]
    subclass = None
    superclass = None
    def __init__(self, value=None, id=None, ratio=None, fruit=None, vegetable=None, name=None, interest=None, category=None, hot_agent=None, agent=None, promoter=None, description=None, range_=None, extensiontype_=None, gds_collector_=None, **kwargs_):
        self.gds_collector_ = gds_collector_
        self.gds_elementtree_node_ = None
        self.original_tagname_ = None
        self.parent_object_ = kwargs_.get('parent_object_')
        self.ns_prefix_ = None
        self.value = _cast(None, value)
        self.value_nsprefix_ = None
        self.id = _cast(int, id)
        self.id_nsprefix_ = None
        self.ratio = _cast(float, ratio)
        self.ratio_nsprefix_ = None
        self.fruit = _cast(None, fruit)
        self.fruit_nsprefix_ = None
        self.vegetable = _cast(None, vegetable)
        self.vegetable_nsprefix_ = None
        self.name = name
        self.name_nsprefix_ = None
        if interest is None:
            self.interest = []
        else:
            self.interest = interest
        self.interest_nsprefix_ = None
        self.category = category
        self.category_nsprefix_ = None
        self.hot_agent = hot_agent
        self.hot_agent_nsprefix_ = None
        if agent is None:
            self.agent = []
        else:
            self.agent = agent
        self.agent_nsprefix_ = None
        if promoter is None:
            self.promoter = []
        else:
            self.promoter = promoter
        self.promoter_nsprefix_ = None
        self.description = description
        self.description_nsprefix_ = None
        self.range_ = range_
        self.validate_RangeType(self.range_)
        self.range__nsprefix_ = None
        self.extensiontype_ = extensiontype_
    def factory(*args_, **kwargs_):
        if CurrentSubclassModule_ is not None:
            subclass = getSubclassFromModule_(
                CurrentSubclassModule_, personType)
            if subclass is not None:
                return subclass(*args_, **kwargs_)
        if personType.subclass:
            return personType.subclass(*args_, **kwargs_)
        else:
            return personType(*args_, **kwargs_)
    factory = staticmethod(factory)
    def get_ns_prefix_(self):
        return self.ns_prefix_
    def set_ns_prefix_(self, ns_prefix):
        self.ns_prefix_ = ns_prefix
    def get_name(self):
        return self.name
    def set_name(self, name):
        self.name = name
    def get_interest(self):
        return self.interest
    def set_interest(self, interest):
        self.interest = interest
    def add_interest(self, value):
        self.interest.append(value)
    def insert_interest_at(self, index, value):
        self.interest.insert(index, value)
    def replace_interest_at(self, index, value):
        self.interest[index] = value
    def get_category(self):
        return self.category
    def set_category(self, category):
        self.category = category
    def get_hot_agent(self):
        return self.hot_agent
    def set_hot_agent(self, hot_agent):
        self.hot_agent = hot_agent
    def get_agent(self):
        return self.agent
    def set_agent(self, agent):
        self.agent = agent
    def add_agent(self, value):
        self.agent.append(value)
    def insert_agent_at(self, index, value):
        self.agent.insert(index, value)
    def replace_agent_at(self, index, value):
        self.agent[index] = value
    def get_promoter(self):
        return self.promoter
    def set_promoter(self, promoter):
        self.promoter = promoter
    def add_promoter(self, value):
        self.promoter.append(value)
    def insert_promoter_at(self, index, value):
        self.promoter.insert(index, value)
    def replace_promoter_at(self, index, value):
        self.promoter[index] = value
    def get_description(self):
        return self.description
    def set_description(self, description):
        self.description = description
    def get_range(self):
        return self.range_
    def set_range(self, range_):
        self.range_ = range_
    def get_value(self):
        return self.value
    def set_value(self, value):
        self.value = value
    def get_id(self):
        return self.id
    def set_id(self, id):
        self.id = id
    def get_ratio(self):
        return self.ratio
    def set_ratio(self, ratio):
        self.ratio = ratio
    def get_fruit(self):
        return self.fruit
    def set_fruit(self, fruit):
        self.fruit = fruit
    def get_vegetable(self):
        return self.vegetable
    def set_vegetable(self, vegetable):
        self.vegetable = vegetable
    def get_extensiontype_(self): return self.extensiontype_
    def set_extensiontype_(self, extensiontype_): self.extensiontype_ = extensiontype_
    def validate_RangeType(self, value):
        result = True
        # Validate type RangeType, a restriction on xs:integer.
        if value is not None and Validate_simpletypes_ and self.gds_collector_ is not None:
            if not isinstance(value, int):
                lineno = self.gds_get_node_lineno_()
                self.gds_collector_.add_message('Value "%(value)s"%(lineno)s is not of the correct base simple type (int)' % {"value": value, "lineno": lineno, })
                return False
            pass
        return result
    def _hasContent(self):
        if (
            self.name is not None or
            self.interest or
            self.category is not None or
            self.hot_agent is not None or
            self.agent or
            self.promoter or
            self.description is not None or
            self.range_ is not None
        ):
            return True
        else:
            return False
    def to_etree(self, parent_element=None, name_='personType', mapping_=None, reverse_mapping_=None, nsmap_=None):
        if parent_element is None:
            element = etree_.Element(name_, nsmap=nsmap_)
        else:
            element = etree_.SubElement(parent_element, name_, nsmap=nsmap_)
        if self.extensiontype_ is not None:
            element.set('{http://www.w3.org/2001/XMLSchema-instance}type', self.extensiontype_)
        if self.value is not None:
            element.set('value', self.gds_format_string(self.value))
        if self.id is not None:
            element.set('id', self.gds_format_integer(self.id))
        if self.ratio is not None:
            element.set('ratio', self.gds_format_float(self.ratio))
        if self.fruit is not None:
            element.set('fruit', self.gds_format_string(self.fruit))
        if self.vegetable is not None:
            element.set('vegetable', self.gds_format_string(self.vegetable))
        if self.name is not None:
            name_ = self.name
            etree_.SubElement(element, 'name').text = self.gds_format_string(name_)
        for interest_ in self.interest:
            etree_.SubElement(element, 'interest').text = self.gds_format_string(interest_)
        if self.category is not None:
            category_ = self.category
            etree_.SubElement(element, 'category').text = self.gds_format_integer(category_)
        if self.hot_agent is not None:
            hot_agent_ = self.hot_agent
            hot_agent_.to_etree(element, name_='hot.agent', mapping_=mapping_, reverse_mapping_=reverse_mapping_, nsmap_=nsmap_)
        for agent_ in self.agent:
            agent_.to_etree(element, name_='agent', mapping_=mapping_, reverse_mapping_=reverse_mapping_, nsmap_=nsmap_)
        for promoter_ in self.promoter:
            promoter_.to_etree(element, name_='promoter', mapping_=mapping_, reverse_mapping_=reverse_mapping_, nsmap_=nsmap_)
        if self.description is not None:
            description_ = self.description
            etree_.SubElement(element, 'description').text = self.gds_format_string(description_)
        if self.range_ is not None:
            range__ = self.range_
            etree_.SubElement(element, 'range').text = self.gds_format_integer(range__)
        if mapping_ is not None:
            mapping_[id(self)] = element
        if reverse_mapping_ is not None:
            reverse_mapping_[element] = self
        return element
    def build(self, node, gds_collector_=None):
        self.gds_collector_ = gds_collector_
        if SaveElementTreeNode:
            self.gds_elementtree_node_ = node
        already_processed = set()
        self.ns_prefix_ = node.prefix
        self._buildAttributes(node, node.attrib, already_processed)
        for child in node:
            nodeName_ = Tag_pattern_.match(child.tag).groups()[-1]
            self._buildChildren(child, node, nodeName_, gds_collector_=gds_collector_)
        return self
    def _buildAttributes(self, node, attrs, already_processed):
        value = find_attr_value_('value', node)
        if value is not None and 'value' not in already_processed:
            already_processed.add('value')
            self.value = value
        value = find_attr_value_('id', node)
        if value is not None and 'id' not in already_processed:
            already_processed.add('id')
            self.id = self.gds_parse_integer(value, node, 'id')
        value = find_attr_value_('ratio', node)
        if value is not None and 'ratio' not in already_processed:
            already_processed.add('ratio')
            value = self.gds_parse_float(value, node, 'ratio')
            self.ratio = value
        value = find_attr_value_('fruit', node)
        if value is not None and 'fruit' not in already_processed:
            already_processed.add('fruit')
            self.fruit = value
        value = find_attr_value_('vegetable', node)
        if value is not None and 'vegetable' not in already_processed:
            already_processed.add('vegetable')
            self.vegetable = value
        value = find_attr_value_('xsi:type', node)
        if value is not None and 'xsi:type' not in already_processed:
            already_processed.add('xsi:type')
            self.extensiontype_ = value
    def _buildChildren(self, child_, node, nodeName_, fromsubclass_=False, gds_collector_=None):
        if nodeName_ == 'name':
            value_ = child_.text
            value_ = self.gds_parse_string(value_, node, 'name')
            value_ = self.gds_validate_string(value_, node, 'name')
            self.name = value_
            self.name_nsprefix_ = child_.prefix
        elif nodeName_ == 'interest':
            value_ = child_.text
            value_ = self.gds_parse_string(value_, node, 'interest')
            value_ = self.gds_validate_string(value_, node, 'interest')
            self.interest.append(value_)
            self.interest_nsprefix_ = child_.prefix
        elif nodeName_ == 'category' and child_.text:
            sval_ = child_.text
            ival_ = self.gds_parse_integer(sval_, node, 'category')
            ival_ = self.gds_validate_integer(ival_, node, 'category')
            self.category = ival_
            self.category_nsprefix_ = child_.prefix
        elif nodeName_ == 'hot.agent':
            obj_ = hot_agent.factory(parent_object_=self)
            obj_.build(child_, gds_collector_=gds_collector_)
            self.hot_agent = obj_
            obj_.original_tagname_ = 'hot.agent'
        elif nodeName_ == 'agent':
            class_obj_ = self.get_class_obj_(child_, agentType)
            obj_ = class_obj_.factory(parent_object_=self)
            obj_.build(child_, gds_collector_=gds_collector_)
            self.agent.append(obj_)
            obj_.original_tagname_ = 'agent'
        elif nodeName_ == 'promoter':
            obj_ = boosterType.factory(parent_object_=self)
            obj_.build(child_, gds_collector_=gds_collector_)
            self.promoter.append(obj_)
            obj_.original_tagname_ = 'promoter'
        elif nodeName_ == 'description':
            value_ = child_.text
            value_ = self.gds_parse_string(value_, node, 'description')
            value_ = self.gds_validate_string(value_, node, 'description')
            self.description = value_
            self.description_nsprefix_ = child_.prefix
        elif nodeName_ == 'range' and child_.text:
            sval_ = child_.text
            ival_ = self.gds_parse_integer(sval_, node, 'range')
            ival_ = self.gds_validate_integer(ival_, node, 'range')
            self.range_ = ival_
            self.range_nsprefix_ = child_.prefix
            # validate type RangeType
            self.validate_RangeType(self.range_)
# end class personType


class specialperson(personType):
    __hash__ = GeneratedsSuper.__hash__
    member_data_items_ = [
    ]
    subclass = None
    superclass = personType
    def __init__(self, value=None, id=None, ratio=None, fruit=None, vegetable=None, name=None, interest=None, category=None, hot_agent=None, agent=None, promoter=None, description=None, range_=None, gds_collector_=None, **kwargs_):
        self.gds_collector_ = gds_collector_
        self.gds_elementtree_node_ = None
        self.original_tagname_ = None
        self.parent_object_ = kwargs_.get('parent_object_')
        self.ns_prefix_ = None
        super(globals().get("specialperson"), self).__init__(value, id, ratio, fruit, vegetable, name, interest, category, hot_agent, agent, promoter, description, range_,  **kwargs_)
    def factory(*args_, **kwargs_):
        if CurrentSubclassModule_ is not None:
            subclass = getSubclassFromModule_(
                CurrentSubclassModule_, specialperson)
            if subclass is not None:
                return subclass(*args_, **kwargs_)
        if specialperson.subclass:
            return specialperson.subclass(*args_, **kwargs_)
        else:
            return specialperson(*args_, **kwargs_)
    factory = staticmethod(factory)
    def get_ns_prefix_(self):
        return self.ns_prefix_
    def set_ns_prefix_(self, ns_prefix):
        self.ns_prefix_ = ns_prefix
    def _hasContent(self):
        if (
            super(specialperson, self)._hasContent()
        ):
            return True
        else:
            return False
    def to_etree(self, parent_element=None, name_='specialperson', mapping_=None, reverse_mapping_=None, nsmap_=None):
        element = super(specialperson, self).to_etree(parent_element, name_, mapping_, reverse_mapping_, nsmap_)
        if mapping_ is not None:
            mapping_[id(self)] = element
        if reverse_mapping_ is not None:
            reverse_mapping_[element] = self
        return element
    def build(self, node, gds_collector_=None):
        self.gds_collector_ = gds_collector_
        if SaveElementTreeNode:
            self.gds_elementtree_node_ = node
        already_processed = set()
        self.ns_prefix_ = node.prefix
        self._buildAttributes(node, node.attrib, already_processed)
        for child in node:
            nodeName_ = Tag_pattern_.match(child.tag).groups()[-1]
            self._buildChildren(child, node, nodeName_, gds_collector_=gds_collector_)
        return self
    def _buildAttributes(self, node, attrs, already_processed):
        super(specialperson, self)._buildAttributes(node, attrs, already_processed)
    def _buildChildren(self, child_, node, nodeName_, fromsubclass_=False, gds_collector_=None):
        super(specialperson, self)._buildChildren(child_, node, nodeName_, True)
        pass
# end class specialperson


class programmerType(personType):
    __hash__ = GeneratedsSuper.__hash__
    member_data_items_ = [
        MemberSpec_('language', 'xs:string', 0, 1, {'use': 'optional', 'name': 'language'}),
        MemberSpec_('area', 'xs:string', 0, 1, {'use': 'optional', 'name': 'area'}),
        MemberSpec_('attrposint', 'xs:positiveInteger', 0, 1, {'use': 'optional', 'name': 'attrposint'}),
        MemberSpec_('attrnonposint', 'xs:nonPositiveInteger', 0, 1, {'use': 'optional', 'name': 'attrnonposint'}),
        MemberSpec_('attrnegint', 'xs:negativeInteger', 0, 1, {'use': 'optional', 'name': 'attrnegint'}),
        MemberSpec_('attrnonnegint', 'xs:nonNegativeInteger', 0, 1, {'use': 'optional', 'name': 'attrnonnegint'}),
        MemberSpec_('email', 'xs:string', 0, 0, {'name': 'email', 'type': 'xs:string'}, None),
        MemberSpec_('elposint', 'xs:positiveInteger', 0, 0, {'name': 'elposint', 'type': 'xs:positiveInteger'}, None),
        MemberSpec_('elnonposint', 'xs:nonPositiveInteger', 0, 0, {'name': 'elnonposint', 'type': 'xs:nonPositiveInteger'}, None),
        MemberSpec_('elnegint', 'xs:negativeInteger', 0, 0, {'name': 'elnegint', 'type': 'xs:negativeInteger'}, None),
        MemberSpec_('elnonnegint', 'xs:nonNegativeInteger', 0, 0, {'name': 'elnonnegint', 'type': 'xs:nonNegativeInteger'}, None),
        MemberSpec_('eldate', 'xs:date', 0, 0, {'name': 'eldate', 'type': 'xs:date'}, None),
        MemberSpec_('eldatetime', 'xs:dateTime', 0, 0, {'name': 'eldatetime', 'type': 'xs:dateTime'}, None),
        MemberSpec_('eldatetime1', 'xs:dateTime', 0, 0, {'name': 'eldatetime1', 'type': 'xs:dateTime'}, None),
        MemberSpec_('eltoken', 'xs:token', 0, 0, {'name': 'eltoken', 'type': 'xs:token'}, None),
        MemberSpec_('elshort', 'xs:short', 0, 0, {'name': 'elshort', 'type': 'xs:short'}, None),
        MemberSpec_('ellong', 'xs:long', 0, 0, {'name': 'ellong', 'type': 'xs:long'}, None),
        MemberSpec_('elparam', 'paramType', 0, 0, {'name': 'elparam', 'type': 'paramType'}, None),
        MemberSpec_('elarraytypes', ['ArrayTypes', 'xs:NMTOKEN'], 0, 0, {'name': 'elarraytypes', 'type': 'xs:NMTOKEN'}, None),
    ]
    subclass = None
    superclass = personType
    def __init__(self, value=None, id=None, ratio=None, fruit=None, vegetable=None, name=None, interest=None, category=None, hot_agent=None, agent=None, promoter=None, description=None, range_=None, language=None, area=None, attrposint=None, attrnonposint=None, attrnegint=None, attrnonnegint=None, email=None, elposint=None, elnonposint=None, elnegint=None, elnonnegint=None, eldate=None, eldatetime=None, eldatetime1=None, eltoken=None, elshort=None, ellong=None, elparam=None, elarraytypes=None, extensiontype_=None, gds_collector_=None, **kwargs_):
        self.gds_collector_ = gds_collector_
        self.gds_elementtree_node_ = None
        self.original_tagname_ = None
        self.parent_object_ = kwargs_.get('parent_object_')
        self.ns_prefix_ = None
        super(globals().get("programmerType"), self).__init__(value, id, ratio, fruit, vegetable, name, interest, category, hot_agent, agent, promoter, description, range_, extensiontype_,  **kwargs_)
        self.language = _cast(None, language)
        self.language_nsprefix_ = None
        self.area = _cast(None, area)
        self.area_nsprefix_ = None
        self.attrposint = _cast(int, attrposint)
        self.attrposint_nsprefix_ = None
        self.attrnonposint = _cast(int, attrnonposint)
        self.attrnonposint_nsprefix_ = None
        self.attrnegint = _cast(int, attrnegint)
        self.attrnegint_nsprefix_ = None
        self.attrnonnegint = _cast(int, attrnonnegint)
        self.attrnonnegint_nsprefix_ = None
        self.email = email
        self.email_nsprefix_ = None
        self.elposint = elposint
        self.elposint_nsprefix_ = None
        self.elnonposint = elnonposint
        self.elnonposint_nsprefix_ = None
        self.elnegint = elnegint
        self.elnegint_nsprefix_ = None
        self.elnonnegint = elnonnegint
        self.elnonnegint_nsprefix_ = None
        if isinstance(eldate, BaseStrType_):
            initvalue_ = datetime_.datetime.strptime(eldate, '%Y-%m-%d').date()
        else:
            initvalue_ = eldate
        self.eldate = initvalue_
        self.eldate_nsprefix_ = None
        if isinstance(eldatetime, BaseStrType_):
            initvalue_ = datetime_.datetime.strptime(eldatetime, '%Y-%m-%dT%H:%M:%S')
        else:
            initvalue_ = eldatetime
        self.eldatetime = initvalue_
        self.eldatetime_nsprefix_ = None
        if isinstance(eldatetime1, BaseStrType_):
            initvalue_ = datetime_.datetime.strptime(eldatetime1, '%Y-%m-%dT%H:%M:%S')
        else:
            initvalue_ = eldatetime1
        self.eldatetime1 = initvalue_
        self.eldatetime1_nsprefix_ = None
        self.eltoken = eltoken
        self.eltoken_nsprefix_ = None
        self.elshort = elshort
        self.elshort_nsprefix_ = None
        self.ellong = ellong
        self.ellong_nsprefix_ = None
        self.elparam = elparam
        self.elparam_nsprefix_ = None
        self.elarraytypes = elarraytypes
        self.validate_ArrayTypes(self.elarraytypes)
        self.elarraytypes_nsprefix_ = None
        self.extensiontype_ = extensiontype_
    def factory(*args_, **kwargs_):
        if CurrentSubclassModule_ is not None:
            subclass = getSubclassFromModule_(
                CurrentSubclassModule_, programmerType)
            if subclass is not None:
                return subclass(*args_, **kwargs_)
        if programmerType.subclass:
            return programmerType.subclass(*args_, **kwargs_)
        else:
            return programmerType(*args_, **kwargs_)
    factory = staticmethod(factory)
    def get_ns_prefix_(self):
        return self.ns_prefix_
    def set_ns_prefix_(self, ns_prefix):
        self.ns_prefix_ = ns_prefix
    def get_email(self):
        return self.email
    def set_email(self, email):
        self.email = email
    def get_elposint(self):
        return self.elposint
    def set_elposint(self, elposint):
        self.elposint = elposint
    def get_elnonposint(self):
        return self.elnonposint
    def set_elnonposint(self, elnonposint):
        self.elnonposint = elnonposint
    def get_elnegint(self):
        return self.elnegint
    def set_elnegint(self, elnegint):
        self.elnegint = elnegint
    def get_elnonnegint(self):
        return self.elnonnegint
    def set_elnonnegint(self, elnonnegint):
        self.elnonnegint = elnonnegint
    def get_eldate(self):
        return self.eldate
    def set_eldate(self, eldate):
        self.eldate = eldate
    def get_eldatetime(self):
        return self.eldatetime
    def set_eldatetime(self, eldatetime):
        self.eldatetime = eldatetime
    def get_eldatetime1(self):
        return self.eldatetime1
    def set_eldatetime1(self, eldatetime1):
        self.eldatetime1 = eldatetime1
    def get_eltoken(self):
        return self.eltoken
    def set_eltoken(self, eltoken):
        self.eltoken = eltoken
    def get_elshort(self):
        return self.elshort
    def set_elshort(self, elshort):
        self.elshort = elshort
    def get_ellong(self):
        return self.ellong
    def set_ellong(self, ellong):
        self.ellong = ellong
    def get_elparam(self):
        return self.elparam
    def set_elparam(self, elparam):
        self.elparam = elparam
    def get_elarraytypes(self):
        return self.elarraytypes
    def set_elarraytypes(self, elarraytypes):
        self.elarraytypes = elarraytypes
    def get_language(self):
        return self.language
    def set_language(self, language):
        self.language = language
    def get_area(self):
        return self.area
    def set_area(self, area):
        self.area = area
    def get_attrposint(self):
        return self.attrposint
    def set_attrposint(self, attrposint):
        self.attrposint = attrposint
    def get_attrnonposint(self):
        return self.attrnonposint
    def set_attrnonposint(self, attrnonposint):
        self.attrnonposint = attrnonposint
    def get_attrnegint(self):
        return self.attrnegint
    def set_attrnegint(self, attrnegint):
        self.attrnegint = attrnegint
    def get_attrnonnegint(self):
        return self.attrnonnegint
    def set_attrnonnegint(self, attrnonnegint):
        self.attrnonnegint = attrnonnegint
    def get_extensiontype_(self): return self.extensiontype_
    def set_extensiontype_(self, extensiontype_): self.extensiontype_ = extensiontype_
    def validate_ArrayTypes(self, value):
        result = True
        # Validate type ArrayTypes, a restriction on xs:NMTOKEN.
        if value is not None and Validate_simpletypes_ and self.gds_collector_ is not None:
            if not isinstance(value, str):
                lineno = self.gds_get_node_lineno_()
                self.gds_collector_.add_message('Value "%(value)s"%(lineno)s is not of the correct base simple type (str)' % {"value": value, "lineno": lineno, })
                return False
            value = value
            enumerations = ['float', 'int', 'Name', 'token']
            if value not in enumerations:
                lineno = self.gds_get_node_lineno_()
                self.gds_collector_.add_message('Value "%(value)s"%(lineno)s does not match xsd enumeration restriction on ArrayTypes' % {"value" : encode_str_2_3(value), "lineno": lineno} )
                result = False
        return result
    def _hasContent(self):
        if (
            self.email is not None or
            self.elposint is not None or
            self.elnonposint is not None or
            self.elnegint is not None or
            self.elnonnegint is not None or
            self.eldate is not None or
            self.eldatetime is not None or
            self.eldatetime1 is not None or
            self.eltoken is not None or
            self.elshort is not None or
            self.ellong is not None or
            self.elparam is not None or
            self.elarraytypes is not None or
            super(programmerType, self)._hasContent()
        ):
            return True
        else:
            return False
    def to_etree(self, parent_element=None, name_='programmerType', mapping_=None, reverse_mapping_=None, nsmap_=None):
        element = super(programmerType, self).to_etree(parent_element, name_, mapping_, reverse_mapping_, nsmap_)
        if self.extensiontype_ is not None:
            element.set('{http://www.w3.org/2001/XMLSchema-instance}type', self.extensiontype_)
        if self.language is not None:
            element.set('language', self.gds_format_string(self.language))
        if self.area is not None:
            element.set('area', self.gds_format_string(self.area))
        if self.attrposint is not None:
            element.set('attrposint', self.gds_format_integer(self.attrposint))
        if self.attrnonposint is not None:
            element.set('attrnonposint', self.gds_format_integer(self.attrnonposint))
        if self.attrnegint is not None:
            element.set('attrnegint', self.gds_format_integer(self.attrnegint))
        if self.attrnonnegint is not None:
            element.set('attrnonnegint', self.gds_format_integer(self.attrnonnegint))
        if self.email is not None:
            email_ = self.email
            etree_.SubElement(element, 'email').text = self.gds_format_string(email_)
        if self.elposint is not None:
            elposint_ = self.elposint
            etree_.SubElement(element, 'elposint').text = self.gds_format_integer(elposint_)
        if self.elnonposint is not None:
            elnonposint_ = self.elnonposint
            etree_.SubElement(element, 'elnonposint').text = self.gds_format_integer(elnonposint_)
        if self.elnegint is not None:
            elnegint_ = self.elnegint
            etree_.SubElement(element, 'elnegint').text = self.gds_format_integer(elnegint_)
        if self.elnonnegint is not None:
            elnonnegint_ = self.elnonnegint
            etree_.SubElement(element, 'elnonnegint').text = self.gds_format_integer(elnonnegint_)
        if self.eldate is not None:
            eldate_ = self.eldate
            etree_.SubElement(element, 'eldate').text = self.gds_format_date(eldate_)
        if self.eldatetime is not None:
            eldatetime_ = self.eldatetime
            etree_.SubElement(element, 'eldatetime').text = self.gds_format_datetime(eldatetime_)
        if self.eldatetime1 is not None:
            eldatetime1_ = self.eldatetime1
            etree_.SubElement(element, 'eldatetime1').text = self.gds_format_datetime(eldatetime1_)
        if self.eltoken is not None:
            eltoken_ = self.eltoken
            etree_.SubElement(element, 'eltoken').text = self.gds_format_string(eltoken_)
        if self.elshort is not None:
            elshort_ = self.elshort
            etree_.SubElement(element, 'elshort').text = self.gds_format_integer(elshort_)
        if self.ellong is not None:
            ellong_ = self.ellong
            etree_.SubElement(element, 'ellong').text = self.gds_format_integer(ellong_)
        if self.elparam is not None:
            elparam_ = self.elparam
            elparam_.to_etree(element, name_='elparam', mapping_=mapping_, reverse_mapping_=reverse_mapping_, nsmap_=nsmap_)
        if self.elarraytypes is not None:
            elarraytypes_ = self.elarraytypes
            etree_.SubElement(element, 'elarraytypes').text = self.gds_format_string(elarraytypes_)
        if mapping_ is not None:
            mapping_[id(self)] = element
        if reverse_mapping_ is not None:
            reverse_mapping_[element] = self
        return element
    def build(self, node, gds_collector_=None):
        self.gds_collector_ = gds_collector_
        if SaveElementTreeNode:
            self.gds_elementtree_node_ = node
        already_processed = set()
        self.ns_prefix_ = node.prefix
        self._buildAttributes(node, node.attrib, already_processed)
        for child in node:
            nodeName_ = Tag_pattern_.match(child.tag).groups()[-1]
            self._buildChildren(child, node, nodeName_, gds_collector_=gds_collector_)
        return self
    def _buildAttributes(self, node, attrs, already_processed):
        value = find_attr_value_('language', node)
        if value is not None and 'language' not in already_processed:
            already_processed.add('language')
            self.language = value
        value = find_attr_value_('area', node)
        if value is not None and 'area' not in already_processed:
            already_processed.add('area')
            self.area = value
        value = find_attr_value_('attrposint', node)
        if value is not None and 'attrposint' not in already_processed:
            already_processed.add('attrposint')
            self.attrposint = self.gds_parse_integer(value, node, 'attrposint')
            if self.attrposint <= 0:
                raise_parse_error(node, 'Invalid PositiveInteger')
        value = find_attr_value_('attrnonposint', node)
        if value is not None and 'attrnonposint' not in already_processed:
            already_processed.add('attrnonposint')
            self.attrnonposint = self.gds_parse_integer(value, node, 'attrnonposint')
            if self.attrnonposint > 0:
                raise_parse_error(node, 'Invalid NonPositiveInteger')
        value = find_attr_value_('attrnegint', node)
        if value is not None and 'attrnegint' not in already_processed:
            already_processed.add('attrnegint')
            self.attrnegint = self.gds_parse_integer(value, node, 'attrnegint')
            if self.attrnegint >= 0:
                raise_parse_error(node, 'Invalid NegativeInteger')
        value = find_attr_value_('attrnonnegint', node)
        if value is not None and 'attrnonnegint' not in already_processed:
            already_processed.add('attrnonnegint')
            self.attrnonnegint = self.gds_parse_integer(value, node, 'attrnonnegint')
            if self.attrnonnegint < 0:
                raise_parse_error(node, 'Invalid NonNegativeInteger')
        value = find_attr_value_('xsi:type', node)
        if value is not None and 'xsi:type' not in already_processed:
            already_processed.add('xsi:type')
            self.extensiontype_ = value
        super(programmerType, self)._buildAttributes(node, attrs, already_processed)
    def _buildChildren(self, child_, node, nodeName_, fromsubclass_=False, gds_collector_=None):
        if nodeName_ == 'email':
            value_ = child_.text
            value_ = self.gds_parse_string(value_, node, 'email')
            value_ = self.gds_validate_string(value_, node, 'email')
            self.email = value_
            self.email_nsprefix_ = child_.prefix
        elif nodeName_ == 'elposint' and child_.text:
            sval_ = child_.text
            ival_ = self.gds_parse_integer(sval_, node, 'elposint')
            if ival_ <= 0:
                raise_parse_error(child_, 'requires positiveInteger')
            ival_ = self.gds_validate_integer(ival_, node, 'elposint')
            self.elposint = ival_
            self.elposint_nsprefix_ = child_.prefix
        elif nodeName_ == 'elnonposint' and child_.text:
            sval_ = child_.text
            ival_ = self.gds_parse_integer(sval_, node, 'elnonposint')
            if ival_ > 0:
                raise_parse_error(child_, 'requires nonPositiveInteger')
            ival_ = self.gds_validate_integer(ival_, node, 'elnonposint')
            self.elnonposint = ival_
            self.elnonposint_nsprefix_ = child_.prefix
        elif nodeName_ == 'elnegint' and child_.text:
            sval_ = child_.text
            ival_ = self.gds_parse_integer(sval_, node, 'elnegint')
            if ival_ >= 0:
                raise_parse_error(child_, 'requires negativeInteger')
            ival_ = self.gds_validate_integer(ival_, node, 'elnegint')
            self.elnegint = ival_
            self.elnegint_nsprefix_ = child_.prefix
        elif nodeName_ == 'elnonnegint' and child_.text:
            sval_ = child_.text
            ival_ = self.gds_parse_integer(sval_, node, 'elnonnegint')
            if ival_ < 0:
                raise_parse_error(child_, 'requires nonNegativeInteger')
            ival_ = self.gds_validate_integer(ival_, node, 'elnonnegint')
            self.elnonnegint = ival_
            self.elnonnegint_nsprefix_ = child_.prefix
        elif nodeName_ == 'eldate':
            sval_ = child_.text
            dval_ = self.gds_parse_date(sval_)
            self.eldate = dval_
            self.eldate_nsprefix_ = child_.prefix
        elif nodeName_ == 'eldatetime':
            sval_ = child_.text
            dval_ = self.gds_parse_datetime(sval_)
            self.eldatetime = dval_
            self.eldatetime_nsprefix_ = child_.prefix
        elif nodeName_ == 'eldatetime1':
            sval_ = child_.text
            dval_ = self.gds_parse_datetime(sval_)
            self.eldatetime1 = dval_
            self.eldatetime1_nsprefix_ = child_.prefix
        elif nodeName_ == 'eltoken':
            value_ = child_.text
            if value_:
                value_ = re_.sub(String_cleanup_pat_, " ", value_).strip()
            else:
                value_ = ""
            value_ = self.gds_parse_string(value_, node, 'eltoken')
            value_ = self.gds_validate_string(value_, node, 'eltoken')
            self.eltoken = value_
            self.eltoken_nsprefix_ = child_.prefix
        elif nodeName_ == 'elshort' and child_.text:
            sval_ = child_.text
            ival_ = self.gds_parse_integer(sval_, node, 'elshort')
            ival_ = self.gds_validate_integer(ival_, node, 'elshort')
            self.elshort = ival_
            self.elshort_nsprefix_ = child_.prefix
        elif nodeName_ == 'ellong' and child_.text:
            sval_ = child_.text
            ival_ = self.gds_parse_integer(sval_, node, 'ellong')
            ival_ = self.gds_validate_integer(ival_, node, 'ellong')
            self.ellong = ival_
            self.ellong_nsprefix_ = child_.prefix
        elif nodeName_ == 'elparam':
            obj_ = paramType.factory(parent_object_=self)
            obj_.build(child_, gds_collector_=gds_collector_)
            self.elparam = obj_
            obj_.original_tagname_ = 'elparam'
        elif nodeName_ == 'elarraytypes':
            value_ = child_.text
            value_ = self.gds_parse_string(value_, node, 'elarraytypes')
            value_ = self.gds_validate_string(value_, node, 'elarraytypes')
            self.elarraytypes = value_
            self.elarraytypes_nsprefix_ = child_.prefix
            # validate type ArrayTypes
            self.validate_ArrayTypes(self.elarraytypes)
        super(programmerType, self)._buildChildren(child_, node, nodeName_, True)
# end class programmerType


class paramType(GeneratedsSuper):
    __hash__ = GeneratedsSuper.__hash__
    member_data_items_ = [
        MemberSpec_('id', 'xs:string', 0, 1, {'use': 'optional', 'name': 'id'}),
        MemberSpec_('name', 'xs:NCName', 0, 1, {'use': 'optional', 'name': 'name'}),
        MemberSpec_('sid', 'xs:NCName', 0, 1, {'use': 'optional', 'name': 'sid'}),
        MemberSpec_('flow', 'FlowType', 0, 1, {'use': 'optional', 'name': 'flow'}),
        MemberSpec_('semantic', 'xs:token', 0, 1, {'use': 'optional', 'name': 'semantic'}),
        MemberSpec_('type_', 'xs:NMTOKEN', 0, 0, {'use': 'required', 'name': 'type_'}),
        MemberSpec_('valueOf_', 'xs:string', 0),
    ]
    subclass = None
    superclass = None
    def __init__(self, id=None, name=None, sid=None, flow=None, semantic=None, type_=None, valueOf_=None, gds_collector_=None, **kwargs_):
        self.gds_collector_ = gds_collector_
        self.gds_elementtree_node_ = None
        self.original_tagname_ = None
        self.parent_object_ = kwargs_.get('parent_object_')
        self.ns_prefix_ = None
        self.id = _cast(None, id)
        self.id_nsprefix_ = None
        self.name = _cast(None, name)
        self.name_nsprefix_ = None
        self.sid = _cast(None, sid)
        self.sid_nsprefix_ = None
        self.flow = _cast(int, flow)
        self.flow_nsprefix_ = None
        self.semantic = _cast(None, semantic)
        self.semantic_nsprefix_ = None
        self.type_ = _cast(None, type_)
        self.type__nsprefix_ = None
        self.valueOf_ = valueOf_
    def factory(*args_, **kwargs_):
        if CurrentSubclassModule_ is not None:
            subclass = getSubclassFromModule_(
                CurrentSubclassModule_, paramType)
            if subclass is not None:
                return subclass(*args_, **kwargs_)
        if paramType.subclass:
            return paramType.subclass(*args_, **kwargs_)
        else:
            return paramType(*args_, **kwargs_)
    factory = staticmethod(factory)
    def get_ns_prefix_(self):
        return self.ns_prefix_
    def set_ns_prefix_(self, ns_prefix):
        self.ns_prefix_ = ns_prefix
    def get_id(self):
        return self.id
    def set_id(self, id):
        self.id = id
    def get_name(self):
        return self.name
    def set_name(self, name):
        self.name = name
    def get_sid(self):
        return self.sid
    def set_sid(self, sid):
        self.sid = sid
    def get_flow(self):
        return self.flow
    def set_flow(self, flow):
        self.flow = flow
    def get_semantic(self):
        return self.semantic
    def set_semantic(self, semantic):
        self.semantic = semantic
    def get_type(self):
        return self.type_
    def set_type(self, type_):
        self.type_ = type_
    def get_valueOf_(self): return self.valueOf_
    def set_valueOf_(self, valueOf_): self.valueOf_ = valueOf_
    def validate_FlowType(self, value):
        # Validate type FlowType, a restriction on xs:integer.
        if value is not None and Validate_simpletypes_ and self.gds_collector_ is not None:
            if not isinstance(value, int):
                lineno = self.gds_get_node_lineno_()
                self.gds_collector_.add_message('Value "%(value)s"%(lineno)s is not of the correct base simple type (int)' % {"value": value, "lineno": lineno, })
                return False
            pass
    def _hasContent(self):
        if (
            (1 if type(self.valueOf_) in [int,float] else self.valueOf_)
        ):
            return True
        else:
            return False
    def to_etree(self, parent_element=None, name_='paramType', mapping_=None, reverse_mapping_=None, nsmap_=None):
        if parent_element is None:
            element = etree_.Element(name_, nsmap=nsmap_)
        else:
            element = etree_.SubElement(parent_element, name_, nsmap=nsmap_)
        if self.id is not None:
            element.set('id', self.gds_format_string(self.id))
        if self.name is not None:
            element.set('name', self.gds_format_string(self.name))
        if self.sid is not None:
            element.set('sid', self.gds_format_string(self.sid))
        if self.flow is not None:
            element.set('flow', self.gds_format_integer(self.flow))
        if self.semantic is not None:
            element.set('semantic', self.gds_format_string(self.semantic))
        if self.type_ is not None:
            element.set('type', self.gds_format_string(self.type_))
        if self._hasContent():
            element.text = self.gds_format_string(self.get_valueOf_())
        if mapping_ is not None:
            mapping_[id(self)] = element
        if reverse_mapping_ is not None:
            reverse_mapping_[element] = self
        return element
    def build(self, node, gds_collector_=None):
        self.gds_collector_ = gds_collector_
        if SaveElementTreeNode:
            self.gds_elementtree_node_ = node
        already_processed = set()
        self.ns_prefix_ = node.prefix
        self._buildAttributes(node, node.attrib, already_processed)
        self.valueOf_ = get_all_text_(node)
        for child in node:
            nodeName_ = Tag_pattern_.match(child.tag).groups()[-1]
            self._buildChildren(child, node, nodeName_, gds_collector_=gds_collector_)
        return self
    def _buildAttributes(self, node, attrs, already_processed):
        value = find_attr_value_('id', node)
        if value is not None and 'id' not in already_processed:
            already_processed.add('id')
            self.id = value
        value = find_attr_value_('name', node)
        if value is not None and 'name' not in already_processed:
            already_processed.add('name')
            self.name = value
        value = find_attr_value_('sid', node)
        if value is not None and 'sid' not in already_processed:
            already_processed.add('sid')
            self.sid = value
        value = find_attr_value_('flow', node)
        if value is not None and 'flow' not in already_processed:
            already_processed.add('flow')
            self.flow = self.gds_parse_integer(value, node, 'flow')
            self.validate_FlowType(self.flow)    # validate type FlowType
        value = find_attr_value_('semantic', node)
        if value is not None and 'semantic' not in already_processed:
            already_processed.add('semantic')
            self.semantic = value
            self.semantic = ' '.join(self.semantic.split())
        value = find_attr_value_('type', node)
        if value is not None and 'type' not in already_processed:
            already_processed.add('type')
            self.type_ = value
    def _buildChildren(self, child_, node, nodeName_, fromsubclass_=False, gds_collector_=None):
        pass
# end class paramType


class python_programmerType(programmerType):
    __hash__ = GeneratedsSuper.__hash__
    member_data_items_ = [
        MemberSpec_('nick_name', 'xs:string', 0, 1, {'use': 'optional', 'name': 'nick-name'}),
        MemberSpec_('drcs_attr', 'xs:string', 0, 1, {'use': 'optional', 'name': 'drcs_attr'}),
        MemberSpec_('gui_developer', 'xs:boolean', 0, 1, {'use': 'optional', 'name': 'gui_developer'}),
        MemberSpec_('favorite_editor', 'xs:string', 0, 0, {'name': 'favorite-editor', 'type': 'xs:string'}, None),
        MemberSpec_('flowvalue', ['FlowType', 'xs:integer'], 0, 0, {'name': 'flowvalue', 'type': 'xs:integer'}, None),
        MemberSpec_('drcs', 'xs:string', 0, 0, {'name': 'drcs', 'type': 'xs:string'}, None),
    ]
    subclass = None
    superclass = programmerType
    def __init__(self, value=None, id=None, ratio=None, fruit=None, vegetable=None, name=None, interest=None, category=None, hot_agent=None, agent=None, promoter=None, description=None, range_=None, language=None, area=None, attrposint=None, attrnonposint=None, attrnegint=None, attrnonnegint=None, email=None, elposint=None, elnonposint=None, elnegint=None, elnonnegint=None, eldate=None, eldatetime=None, eldatetime1=None, eltoken=None, elshort=None, ellong=None, elparam=None, elarraytypes=None, nick_name=None, drcs_attr=None, gui_developer=None, favorite_editor=None, flowvalue=None, drcs=None, gds_collector_=None, **kwargs_):
        self.gds_collector_ = gds_collector_
        self.gds_elementtree_node_ = None
        self.original_tagname_ = None
        self.parent_object_ = kwargs_.get('parent_object_')
        self.ns_prefix_ = None
        super(globals().get("python_programmerType"), self).__init__(value, id, ratio, fruit, vegetable, name, interest, category, hot_agent, agent, promoter, description, range_, language, area, attrposint, attrnonposint, attrnegint, attrnonnegint, email, elposint, elnonposint, elnegint, elnonnegint, eldate, eldatetime, eldatetime1, eltoken, elshort, ellong, elparam, elarraytypes,  **kwargs_)
        self.nick_name = _cast(None, nick_name)
        self.nick_name_nsprefix_ = None
        self.drcs_attr = _cast(None, drcs_attr)
        self.drcs_attr_nsprefix_ = None
        self.gui_developer = _cast(bool, gui_developer)
        self.gui_developer_nsprefix_ = None
        self.favorite_editor = favorite_editor
        self.favorite_editor_nsprefix_ = None
        self.flowvalue = flowvalue
        self.validate_FlowType(self.flowvalue)
        self.flowvalue_nsprefix_ = None
        self.drcs = drcs
        self.drcs_nsprefix_ = None
    def factory(*args_, **kwargs_):
        if CurrentSubclassModule_ is not None:
            subclass = getSubclassFromModule_(
                CurrentSubclassModule_, python_programmerType)
            if subclass is not None:
                return subclass(*args_, **kwargs_)
        if python_programmerType.subclass:
            return python_programmerType.subclass(*args_, **kwargs_)
        else:
            return python_programmerType(*args_, **kwargs_)
    factory = staticmethod(factory)
    def get_ns_prefix_(self):
        return self.ns_prefix_
    def set_ns_prefix_(self, ns_prefix):
        self.ns_prefix_ = ns_prefix
    def get_favorite_editor(self):
        return self.favorite_editor
    def set_favorite_editor(self, favorite_editor):
        self.favorite_editor = favorite_editor
    def get_flowvalue(self):
        return self.flowvalue
    def set_flowvalue(self, flowvalue):
        self.flowvalue = flowvalue
    def get_drcs(self):
        return self.drcs
    def set_drcs(self, drcs):
        self.drcs = drcs
    def get_nick_name(self):
        return self.nick_name
    def set_nick_name(self, nick_name):
        self.nick_name = nick_name
    def get_drcs_attr(self):
        return self.drcs_attr
    def set_drcs_attr(self, drcs_attr):
        self.drcs_attr = drcs_attr
    def get_gui_developer(self):
        return self.gui_developer
    def set_gui_developer(self, gui_developer):
        self.gui_developer = gui_developer
    def validate_FlowType(self, value):
        result = True
        # Validate type FlowType, a restriction on xs:integer.
        if value is not None and Validate_simpletypes_ and self.gds_collector_ is not None:
            if not isinstance(value, int):
                lineno = self.gds_get_node_lineno_()
                self.gds_collector_.add_message('Value "%(value)s"%(lineno)s is not of the correct base simple type (int)' % {"value": value, "lineno": lineno, })
                return False
            pass
        return result
    def _hasContent(self):
        if (
            self.favorite_editor is not None or
            self.flowvalue is not None or
            self.drcs is not None or
            super(python_programmerType, self)._hasContent()
        ):
            return True
        else:
            return False
    def to_etree(self, parent_element=None, name_='python-programmerType', mapping_=None, reverse_mapping_=None, nsmap_=None):
        element = super(python_programmerType, self).to_etree(parent_element, name_, mapping_, reverse_mapping_, nsmap_)
        if self.nick_name is not None:
            element.set('nick-name', self.gds_format_string(self.nick_name))
        if self.drcs_attr is not None:
            element.set('drcs_attr', self.gds_format_string(self.drcs_attr))
        if self.gui_developer is not None:
            element.set('gui_developer', self.gds_format_boolean(self.gui_developer))
        if self.favorite_editor is not None:
            favorite_editor_ = self.favorite_editor
            etree_.SubElement(element, 'favorite-editor').text = self.gds_format_string(favorite_editor_)
        if self.flowvalue is not None:
            flowvalue_ = self.flowvalue
            etree_.SubElement(element, 'flowvalue').text = self.gds_format_integer(flowvalue_)
        if self.drcs is not None:
            drcs_ = self.drcs
            etree_.SubElement(element, 'drcs').text = self.gds_format_string(drcs_)
        if mapping_ is not None:
            mapping_[id(self)] = element
        if reverse_mapping_ is not None:
            reverse_mapping_[element] = self
        return element
    def build(self, node, gds_collector_=None):
        self.gds_collector_ = gds_collector_
        if SaveElementTreeNode:
            self.gds_elementtree_node_ = node
        already_processed = set()
        self.ns_prefix_ = node.prefix
        self._buildAttributes(node, node.attrib, already_processed)
        for child in node:
            nodeName_ = Tag_pattern_.match(child.tag).groups()[-1]
            self._buildChildren(child, node, nodeName_, gds_collector_=gds_collector_)
        return self
    def _buildAttributes(self, node, attrs, already_processed):
        value = find_attr_value_('nick-name', node)
        if value is not None and 'nick-name' not in already_processed:
            already_processed.add('nick-name')
            self.nick_name = value
        value = find_attr_value_('drcs', node)
        if value is not None and 'drcs_attr' not in already_processed:
            already_processed.add('drcs_attr')
            self.drcs_attr = value
        value = find_attr_value_('gui_developer', node)
        if value is not None and 'gui_developer' not in already_processed:
            already_processed.add('gui_developer')
            if value in ('true', '1'):
                self.gui_developer = True
            elif value in ('false', '0'):
                self.gui_developer = False
            else:
                raise_parse_error(node, 'Bad boolean attribute')
        super(python_programmerType, self)._buildAttributes(node, attrs, already_processed)
    def _buildChildren(self, child_, node, nodeName_, fromsubclass_=False, gds_collector_=None):
        if nodeName_ == 'favorite-editor':
            value_ = child_.text
            value_ = self.gds_parse_string(value_, node, 'favorite_editor')
            value_ = self.gds_validate_string(value_, node, 'favorite_editor')
            self.favorite_editor = value_
            self.favorite_editor_nsprefix_ = child_.prefix
        elif nodeName_ == 'flowvalue' and child_.text:
            sval_ = child_.text
            ival_ = self.gds_parse_integer(sval_, node, 'flowvalue')
            ival_ = self.gds_validate_integer(ival_, node, 'flowvalue')
            self.flowvalue = ival_
            self.flowvalue_nsprefix_ = child_.prefix
            # validate type FlowType
            self.validate_FlowType(self.flowvalue)
        elif nodeName_ == 'drcs':
            value_ = child_.text
            value_ = self.gds_parse_string(value_, node, 'drcs')
            value_ = self.gds_validate_string(value_, node, 'drcs')
            self.drcs = value_
            self.drcs_nsprefix_ = child_.prefix
        super(python_programmerType, self)._buildChildren(child_, node, nodeName_, True)
# end class python_programmerType


class java_programmerType(programmerType):
    __hash__ = GeneratedsSuper.__hash__
    member_data_items_ = [
        MemberSpec_('nick_name', 'xs:string', 0, 1, {'use': 'optional', 'name': 'nick-name'}),
        MemberSpec_('status', 'xs:string', 0, 1, {'use': 'optional', 'name': 'status'}),
        MemberSpec_('favorite_editor', 'xs:string', 0, 0, {'name': 'favorite-editor', 'type': 'xs:string'}, None),
        MemberSpec_('datetime1', 'xs:gYear', 0, 0, {'name': 'datetime1', 'type': 'xs:gYear'}, None),
        MemberSpec_('datetime2', 'xs:gYearMonth', 0, 0, {'name': 'datetime2', 'type': 'xs:gYearMonth'}, None),
        MemberSpec_('datetime3', 'xs:gMonth', 0, 0, {'name': 'datetime3', 'type': 'xs:gMonth'}, None),
        MemberSpec_('datetime4', 'xs:gMonthDay', 0, 0, {'name': 'datetime4', 'type': 'xs:gMonthDay'}, None),
        MemberSpec_('datetime5', 'xs:gDay', 0, 0, {'name': 'datetime5', 'type': 'xs:gDay'}, None),
    ]
    subclass = None
    superclass = programmerType
    def __init__(self, value=None, id=None, ratio=None, fruit=None, vegetable=None, name=None, interest=None, category=None, hot_agent=None, agent=None, promoter=None, description=None, range_=None, language=None, area=None, attrposint=None, attrnonposint=None, attrnegint=None, attrnonnegint=None, email=None, elposint=None, elnonposint=None, elnegint=None, elnonnegint=None, eldate=None, eldatetime=None, eldatetime1=None, eltoken=None, elshort=None, ellong=None, elparam=None, elarraytypes=None, nick_name=None, status=None, favorite_editor=None, datetime1=None, datetime2=None, datetime3=None, datetime4=None, datetime5=None, gds_collector_=None, **kwargs_):
        self.gds_collector_ = gds_collector_
        self.gds_elementtree_node_ = None
        self.original_tagname_ = None
        self.parent_object_ = kwargs_.get('parent_object_')
        self.ns_prefix_ = None
        super(globals().get("java_programmerType"), self).__init__(value, id, ratio, fruit, vegetable, name, interest, category, hot_agent, agent, promoter, description, range_, language, area, attrposint, attrnonposint, attrnegint, attrnonnegint, email, elposint, elnonposint, elnegint, elnonnegint, eldate, eldatetime, eldatetime1, eltoken, elshort, ellong, elparam, elarraytypes,  **kwargs_)
        self.nick_name = _cast(None, nick_name)
        self.nick_name_nsprefix_ = None
        self.status = _cast(None, status)
        self.status_nsprefix_ = None
        self.favorite_editor = favorite_editor
        self.favorite_editor_nsprefix_ = None
        self.datetime1 = datetime1
        self.datetime1_nsprefix_ = None
        self.datetime2 = datetime2
        self.datetime2_nsprefix_ = None
        self.datetime3 = datetime3
        self.datetime3_nsprefix_ = None
        self.datetime4 = datetime4
        self.datetime4_nsprefix_ = None
        self.datetime5 = datetime5
        self.datetime5_nsprefix_ = None
    def factory(*args_, **kwargs_):
        if CurrentSubclassModule_ is not None:
            subclass = getSubclassFromModule_(
                CurrentSubclassModule_, java_programmerType)
            if subclass is not None:
                return subclass(*args_, **kwargs_)
        if java_programmerType.subclass:
            return java_programmerType.subclass(*args_, **kwargs_)
        else:
            return java_programmerType(*args_, **kwargs_)
    factory = staticmethod(factory)
    def get_ns_prefix_(self):
        return self.ns_prefix_
    def set_ns_prefix_(self, ns_prefix):
        self.ns_prefix_ = ns_prefix
    def get_favorite_editor(self):
        return self.favorite_editor
    def set_favorite_editor(self, favorite_editor):
        self.favorite_editor = favorite_editor
    def get_datetime1(self):
        return self.datetime1
    def set_datetime1(self, datetime1):
        self.datetime1 = datetime1
    def get_datetime2(self):
        return self.datetime2
    def set_datetime2(self, datetime2):
        self.datetime2 = datetime2
    def get_datetime3(self):
        return self.datetime3
    def set_datetime3(self, datetime3):
        self.datetime3 = datetime3
    def get_datetime4(self):
        return self.datetime4
    def set_datetime4(self, datetime4):
        self.datetime4 = datetime4
    def get_datetime5(self):
        return self.datetime5
    def set_datetime5(self, datetime5):
        self.datetime5 = datetime5
    def get_nick_name(self):
        return self.nick_name
    def set_nick_name(self, nick_name):
        self.nick_name = nick_name
    def get_status(self):
        return self.status
    def set_status(self, status):
        self.status = status
    def _hasContent(self):
        if (
            self.favorite_editor is not None or
            self.datetime1 is not None or
            self.datetime2 is not None or
            self.datetime3 is not None or
            self.datetime4 is not None or
            self.datetime5 is not None or
            super(java_programmerType, self)._hasContent()
        ):
            return True
        else:
            return False
    def to_etree(self, parent_element=None, name_='java-programmerType', mapping_=None, reverse_mapping_=None, nsmap_=None):
        element = super(java_programmerType, self).to_etree(parent_element, name_, mapping_, reverse_mapping_, nsmap_)
        if self.nick_name is not None:
            element.set('nick-name', self.gds_format_string(self.nick_name))
        if self.status is not None:
            element.set('status', self.gds_format_string(self.status))
        if self.favorite_editor is not None:
            favorite_editor_ = self.favorite_editor
            etree_.SubElement(element, 'favorite-editor').text = self.gds_format_string(favorite_editor_)
        if self.datetime1 is not None:
            datetime1_ = self.datetime1
            etree_.SubElement(element, 'datetime1').text = self.gds_format_string(datetime1_)
        if self.datetime2 is not None:
            datetime2_ = self.datetime2
            etree_.SubElement(element, 'datetime2').text = self.gds_format_string(datetime2_)
        if self.datetime3 is not None:
            datetime3_ = self.datetime3
            etree_.SubElement(element, 'datetime3').text = self.gds_format_string(datetime3_)
        if self.datetime4 is not None:
            datetime4_ = self.datetime4
            etree_.SubElement(element, 'datetime4').text = self.gds_format_string(datetime4_)
        if self.datetime5 is not None:
            datetime5_ = self.datetime5
            etree_.SubElement(element, 'datetime5').text = self.gds_format_string(datetime5_)
        if mapping_ is not None:
            mapping_[id(self)] = element
        if reverse_mapping_ is not None:
            reverse_mapping_[element] = self
        return element
    def build(self, node, gds_collector_=None):
        self.gds_collector_ = gds_collector_
        if SaveElementTreeNode:
            self.gds_elementtree_node_ = node
        already_processed = set()
        self.ns_prefix_ = node.prefix
        self._buildAttributes(node, node.attrib, already_processed)
        for child in node:
            nodeName_ = Tag_pattern_.match(child.tag).groups()[-1]
            self._buildChildren(child, node, nodeName_, gds_collector_=gds_collector_)
        return self
    def _buildAttributes(self, node, attrs, already_processed):
        value = find_attr_value_('nick-name', node)
        if value is not None and 'nick-name' not in already_processed:
            already_processed.add('nick-name')
            self.nick_name = value
        value = find_attr_value_('status', node)
        if value is not None and 'status' not in already_processed:
            already_processed.add('status')
            self.status = value
        super(java_programmerType, self)._buildAttributes(node, attrs, already_processed)
    def _buildChildren(self, child_, node, nodeName_, fromsubclass_=False, gds_collector_=None):
        if nodeName_ == 'favorite-editor':
            value_ = child_.text
            value_ = self.gds_parse_string(value_, node, 'favorite_editor')
            value_ = self.gds_validate_string(value_, node, 'favorite_editor')
            self.favorite_editor = value_
            self.favorite_editor_nsprefix_ = child_.prefix
        elif nodeName_ == 'datetime1':
            value_ = child_.text
            value_ = self.gds_parse_string(value_, node, 'datetime1')
            value_ = self.gds_validate_string(value_, node, 'datetime1')
            self.datetime1 = value_
            self.datetime1_nsprefix_ = child_.prefix
        elif nodeName_ == 'datetime2':
            value_ = child_.text
            value_ = self.gds_parse_string(value_, node, 'datetime2')
            value_ = self.gds_validate_string(value_, node, 'datetime2')
            self.datetime2 = value_
            self.datetime2_nsprefix_ = child_.prefix
        elif nodeName_ == 'datetime3':
            value_ = child_.text
            value_ = self.gds_parse_string(value_, node, 'datetime3')
            value_ = self.gds_validate_string(value_, node, 'datetime3')
            self.datetime3 = value_
            self.datetime3_nsprefix_ = child_.prefix
        elif nodeName_ == 'datetime4':
            value_ = child_.text
            value_ = self.gds_parse_string(value_, node, 'datetime4')
            value_ = self.gds_validate_string(value_, node, 'datetime4')
            self.datetime4 = value_
            self.datetime4_nsprefix_ = child_.prefix
        elif nodeName_ == 'datetime5':
            value_ = child_.text
            value_ = self.gds_parse_string(value_, node, 'datetime5')
            value_ = self.gds_validate_string(value_, node, 'datetime5')
            self.datetime5 = value_
            self.datetime5_nsprefix_ = child_.prefix
        super(java_programmerType, self)._buildChildren(child_, node, nodeName_, True)
# end class java_programmerType


class agentType(GeneratedsSuper):
    __hash__ = GeneratedsSuper.__hash__
    member_data_items_ = [
        MemberSpec_('firstname', 'xs:string', 0, 0, {'name': 'firstname', 'type': 'xs:string'}, None),
        MemberSpec_('lastname', 'xs:string', 0, 0, {'name': 'lastname', 'type': 'xs:string'}, None),
        MemberSpec_('priority', 'xs:float', 0, 0, {'name': 'priority', 'type': 'xs:float'}, None),
        MemberSpec_('info', 'infoType', 0, 0, {'name': 'info', 'type': 'infoType'}, None),
        MemberSpec_('vehicle', 'vehicleType', 1, 1, {'maxOccurs': 'unbounded', 'minOccurs': '0', 'name': 'vehicle', 'ref': 'vehicle', 'type': 'vehicle'}, None),
    ]
    subclass = None
    superclass = None
    def __init__(self, firstname=None, lastname=None, priority=None, info=None, vehicle=None, extensiontype_=None, gds_collector_=None, **kwargs_):
        self.gds_collector_ = gds_collector_
        self.gds_elementtree_node_ = None
        self.original_tagname_ = None
        self.parent_object_ = kwargs_.get('parent_object_')
        self.ns_prefix_ = None
        self.firstname = firstname
        self.firstname_nsprefix_ = None
        self.lastname = lastname
        self.lastname_nsprefix_ = None
        self.priority = priority
        self.priority_nsprefix_ = None
        self.info = info
        self.info_nsprefix_ = None
        if vehicle is None:
            self.vehicle = []
        else:
            self.vehicle = vehicle
        self.vehicle_nsprefix_ = None
        self.extensiontype_ = extensiontype_
    def factory(*args_, **kwargs_):
        if CurrentSubclassModule_ is not None:
            subclass = getSubclassFromModule_(
                CurrentSubclassModule_, agentType)
            if subclass is not None:
                return subclass(*args_, **kwargs_)
        if agentType.subclass:
            return agentType.subclass(*args_, **kwargs_)
        else:
            return agentType(*args_, **kwargs_)
    factory = staticmethod(factory)
    def get_ns_prefix_(self):
        return self.ns_prefix_
    def set_ns_prefix_(self, ns_prefix):
        self.ns_prefix_ = ns_prefix
    def get_firstname(self):
        return self.firstname
    def set_firstname(self, firstname):
        self.firstname = firstname
    def get_lastname(self):
        return self.lastname
    def set_lastname(self, lastname):
        self.lastname = lastname
    def get_priority(self):
        return self.priority
    def set_priority(self, priority):
        self.priority = priority
    def get_info(self):
        return self.info
    def set_info(self, info):
        self.info = info
    def get_vehicle(self):
        return self.vehicle
    def set_vehicle(self, vehicle):
        self.vehicle = vehicle
    def add_vehicle(self, value):
        self.vehicle.append(value)
    def insert_vehicle_at(self, index, value):
        self.vehicle.insert(index, value)
    def replace_vehicle_at(self, index, value):
        self.vehicle[index] = value
    def get_extensiontype_(self): return self.extensiontype_
    def set_extensiontype_(self, extensiontype_): self.extensiontype_ = extensiontype_
    def _hasContent(self):
        if (
            self.firstname is not None or
            self.lastname is not None or
            self.priority is not None or
            self.info is not None or
            self.vehicle
        ):
            return True
        else:
            return False
    def to_etree(self, parent_element=None, name_='agentType', mapping_=None, reverse_mapping_=None, nsmap_=None):
        if parent_element is None:
            element = etree_.Element(name_, nsmap=nsmap_)
        else:
            element = etree_.SubElement(parent_element, name_, nsmap=nsmap_)
        if self.extensiontype_ is not None:
            element.set('{http://www.w3.org/2001/XMLSchema-instance}type', self.extensiontype_)
        if self.firstname is not None:
            firstname_ = self.firstname
            etree_.SubElement(element, 'firstname').text = self.gds_format_string(firstname_)
        if self.lastname is not None:
            lastname_ = self.lastname
            etree_.SubElement(element, 'lastname').text = self.gds_format_string(lastname_)
        if self.priority is not None:
            priority_ = self.priority
            etree_.SubElement(element, 'priority').text = self.gds_format_float(priority_)
        if self.info is not None:
            info_ = self.info
            info_.to_etree(element, name_='info', mapping_=mapping_, reverse_mapping_=reverse_mapping_, nsmap_=nsmap_)
        for vehicle_ in self.vehicle:
            vehicle_.to_etree(element, name_='vehicle', mapping_=mapping_, reverse_mapping_=reverse_mapping_, nsmap_=nsmap_)
        if mapping_ is not None:
            mapping_[id(self)] = element
        if reverse_mapping_ is not None:
            reverse_mapping_[element] = self
        return element
    def build(self, node, gds_collector_=None):
        self.gds_collector_ = gds_collector_
        if SaveElementTreeNode:
            self.gds_elementtree_node_ = node
        already_processed = set()
        self.ns_prefix_ = node.prefix
        self._buildAttributes(node, node.attrib, already_processed)
        for child in node:
            nodeName_ = Tag_pattern_.match(child.tag).groups()[-1]
            self._buildChildren(child, node, nodeName_, gds_collector_=gds_collector_)
        return self
    def _buildAttributes(self, node, attrs, already_processed):
        value = find_attr_value_('xsi:type', node)
        if value is not None and 'xsi:type' not in already_processed:
            already_processed.add('xsi:type')
            self.extensiontype_ = value
    def _buildChildren(self, child_, node, nodeName_, fromsubclass_=False, gds_collector_=None):
        if nodeName_ == 'firstname':
            value_ = child_.text
            value_ = self.gds_parse_string(value_, node, 'firstname')
            value_ = self.gds_validate_string(value_, node, 'firstname')
            self.firstname = value_
            self.firstname_nsprefix_ = child_.prefix
        elif nodeName_ == 'lastname':
            value_ = child_.text
            value_ = self.gds_parse_string(value_, node, 'lastname')
            value_ = self.gds_validate_string(value_, node, 'lastname')
            self.lastname = value_
            self.lastname_nsprefix_ = child_.prefix
        elif nodeName_ == 'priority' and child_.text:
            sval_ = child_.text
            fval_ = self.gds_parse_float(sval_, node, 'priority')
            fval_ = self.gds_validate_float(fval_, node, 'priority')
            self.priority = fval_
            self.priority_nsprefix_ = child_.prefix
        elif nodeName_ == 'info':
            obj_ = infoType.factory(parent_object_=self)
            obj_.build(child_, gds_collector_=gds_collector_)
            self.info = obj_
            obj_.original_tagname_ = 'info'
        elif nodeName_ == 'vehicle':
            type_name_ = child_.attrib.get(
                '{http://www.w3.org/2001/XMLSchema-instance}type')
            if type_name_ is None:
                type_name_ = child_.attrib.get('type')
            if type_name_ is not None:
                type_names_ = type_name_.split(':')
                if len(type_names_) == 1:
                    type_name_ = type_names_[0]
                else:
                    type_name_ = type_names_[1]
                class_ = globals()[type_name_]
                obj_ = class_.factory()
                obj_.build(child_, gds_collector_=gds_collector_)
            else:
                raise NotImplementedError(
                    'Class not implemented for <vehicle> element')
            self.vehicle.append(obj_)
            obj_.original_tagname_ = 'vehicle'
# end class agentType


class special_agentType(agentType):
    """special-agentType --
    This is a good kind of agent for testing the generation
    of Python bindings for an XML schema.
    
    """
    __hash__ = GeneratedsSuper.__hash__
    member_data_items_ = [
        MemberSpec_('firstname', 'xs:string', 0, 0, {'name': 'firstname', 'type': 'xs:string'}, None),
        MemberSpec_('lastname', 'xs:string', 0, 0, {'name': 'lastname', 'type': 'xs:string'}, None),
        MemberSpec_('priority', 'xs:float', 0, 0, {'name': 'priority', 'type': 'xs:float'}, None),
        MemberSpec_('info', 'infoType', 0, 0, {'name': 'info', 'type': 'infoType'}, None),
    ]
    subclass = None
    superclass = agentType
    def __init__(self, firstname=None, lastname=None, priority=None, info=None, vehicle=None, gds_collector_=None, **kwargs_):
        self.gds_collector_ = gds_collector_
        self.gds_elementtree_node_ = None
        self.original_tagname_ = None
        self.parent_object_ = kwargs_.get('parent_object_')
        self.ns_prefix_ = None
        super(globals().get("special_agentType"), self).__init__(firstname, lastname, priority, info, vehicle,  **kwargs_)
        self.firstname = firstname
        self.firstname_nsprefix_ = None
        self.lastname = lastname
        self.lastname_nsprefix_ = None
        self.priority = priority
        self.priority_nsprefix_ = None
        self.info = info
        self.info_nsprefix_ = None
    def factory(*args_, **kwargs_):
        if CurrentSubclassModule_ is not None:
            subclass = getSubclassFromModule_(
                CurrentSubclassModule_, special_agentType)
            if subclass is not None:
                return subclass(*args_, **kwargs_)
        if special_agentType.subclass:
            return special_agentType.subclass(*args_, **kwargs_)
        else:
            return special_agentType(*args_, **kwargs_)
    factory = staticmethod(factory)
    def get_ns_prefix_(self):
        return self.ns_prefix_
    def set_ns_prefix_(self, ns_prefix):
        self.ns_prefix_ = ns_prefix
    def get_firstname(self):
        return self.firstname
    def set_firstname(self, firstname):
        self.firstname = firstname
    def get_lastname(self):
        return self.lastname
    def set_lastname(self, lastname):
        self.lastname = lastname
    def get_priority(self):
        return self.priority
    def set_priority(self, priority):
        self.priority = priority
    def get_info(self):
        return self.info
    def set_info(self, info):
        self.info = info
    def _hasContent(self):
        if (
            self.firstname is not None or
            self.lastname is not None or
            self.priority is not None or
            self.info is not None or
            super(special_agentType, self)._hasContent()
        ):
            return True
        else:
            return False
    def to_etree(self, parent_element=None, name_='special-agentType', mapping_=None, reverse_mapping_=None, nsmap_=None):
        element = super(special_agentType, self).to_etree(parent_element, name_, mapping_, reverse_mapping_, nsmap_)
        if self.firstname is not None:
            firstname_ = self.firstname
            etree_.SubElement(element, 'firstname').text = self.gds_format_string(firstname_)
        if self.lastname is not None:
            lastname_ = self.lastname
            etree_.SubElement(element, 'lastname').text = self.gds_format_string(lastname_)
        if self.priority is not None:
            priority_ = self.priority
            etree_.SubElement(element, 'priority').text = self.gds_format_float(priority_)
        if self.info is not None:
            info_ = self.info
            info_.to_etree(element, name_='info', mapping_=mapping_, reverse_mapping_=reverse_mapping_, nsmap_=nsmap_)
        if mapping_ is not None:
            mapping_[id(self)] = element
        if reverse_mapping_ is not None:
            reverse_mapping_[element] = self
        return element
    def build(self, node, gds_collector_=None):
        self.gds_collector_ = gds_collector_
        if SaveElementTreeNode:
            self.gds_elementtree_node_ = node
        already_processed = set()
        self.ns_prefix_ = node.prefix
        self._buildAttributes(node, node.attrib, already_processed)
        for child in node:
            nodeName_ = Tag_pattern_.match(child.tag).groups()[-1]
            self._buildChildren(child, node, nodeName_, gds_collector_=gds_collector_)
        return self
    def _buildAttributes(self, node, attrs, already_processed):
        super(special_agentType, self)._buildAttributes(node, attrs, already_processed)
    def _buildChildren(self, child_, node, nodeName_, fromsubclass_=False, gds_collector_=None):
        if nodeName_ == 'firstname':
            value_ = child_.text
            value_ = self.gds_parse_string(value_, node, 'firstname')
            value_ = self.gds_validate_string(value_, node, 'firstname')
            self.firstname = value_
            self.firstname_nsprefix_ = child_.prefix
        elif nodeName_ == 'lastname':
            value_ = child_.text
            value_ = self.gds_parse_string(value_, node, 'lastname')
            value_ = self.gds_validate_string(value_, node, 'lastname')
            self.lastname = value_
            self.lastname_nsprefix_ = child_.prefix
        elif nodeName_ == 'priority' and child_.text:
            sval_ = child_.text
            fval_ = self.gds_parse_float(sval_, node, 'priority')
            fval_ = self.gds_validate_float(fval_, node, 'priority')
            self.priority = fval_
            self.priority_nsprefix_ = child_.prefix
        elif nodeName_ == 'info':
            obj_ = infoType.factory(parent_object_=self)
            obj_.build(child_, gds_collector_=gds_collector_)
            self.info = obj_
            obj_.original_tagname_ = 'info'
        super(special_agentType, self)._buildChildren(child_, node, nodeName_, True)
# end class special_agentType


class weird_agentType(agentType):
    """weird-agentType --
    This is a good kind of agent for testing the generation
    of Python bindings for an XML schema.
    
    """
    __hash__ = GeneratedsSuper.__hash__
    member_data_items_ = [
        MemberSpec_('firstname', 'xs:string', 0, 0, {'name': 'firstname', 'type': 'xs:string'}, None),
        MemberSpec_('lastname', 'xs:string', 0, 0, {'name': 'lastname', 'type': 'xs:string'}, None),
        MemberSpec_('priority', 'xs:float', 0, 0, {'name': 'priority', 'type': 'xs:float'}, None),
        MemberSpec_('info', 'infoType', 0, 0, {'name': 'info', 'type': 'infoType'}, None),
    ]
    subclass = None
    superclass = agentType
    def __init__(self, firstname=None, lastname=None, priority=None, info=None, vehicle=None, gds_collector_=None, **kwargs_):
        self.gds_collector_ = gds_collector_
        self.gds_elementtree_node_ = None
        self.original_tagname_ = None
        self.parent_object_ = kwargs_.get('parent_object_')
        self.ns_prefix_ = None
        super(globals().get("weird_agentType"), self).__init__(firstname, lastname, priority, info, vehicle,  **kwargs_)
        self.firstname = firstname
        self.firstname_nsprefix_ = None
        self.lastname = lastname
        self.lastname_nsprefix_ = None
        self.priority = priority
        self.priority_nsprefix_ = None
        self.info = info
        self.info_nsprefix_ = None
    def factory(*args_, **kwargs_):
        if CurrentSubclassModule_ is not None:
            subclass = getSubclassFromModule_(
                CurrentSubclassModule_, weird_agentType)
            if subclass is not None:
                return subclass(*args_, **kwargs_)
        if weird_agentType.subclass:
            return weird_agentType.subclass(*args_, **kwargs_)
        else:
            return weird_agentType(*args_, **kwargs_)
    factory = staticmethod(factory)
    def get_ns_prefix_(self):
        return self.ns_prefix_
    def set_ns_prefix_(self, ns_prefix):
        self.ns_prefix_ = ns_prefix
    def get_firstname(self):
        return self.firstname
    def set_firstname(self, firstname):
        self.firstname = firstname
    def get_lastname(self):
        return self.lastname
    def set_lastname(self, lastname):
        self.lastname = lastname
    def get_priority(self):
        return self.priority
    def set_priority(self, priority):
        self.priority = priority
    def get_info(self):
        return self.info
    def set_info(self, info):
        self.info = info
    def _hasContent(self):
        if (
            self.firstname is not None or
            self.lastname is not None or
            self.priority is not None or
            self.info is not None or
            super(weird_agentType, self)._hasContent()
        ):
            return True
        else:
            return False
    def to_etree(self, parent_element=None, name_='weird-agentType', mapping_=None, reverse_mapping_=None, nsmap_=None):
        element = super(weird_agentType, self).to_etree(parent_element, name_, mapping_, reverse_mapping_, nsmap_)
        if self.firstname is not None:
            firstname_ = self.firstname
            etree_.SubElement(element, 'firstname').text = self.gds_format_string(firstname_)
        if self.lastname is not None:
            lastname_ = self.lastname
            etree_.SubElement(element, 'lastname').text = self.gds_format_string(lastname_)
        if self.priority is not None:
            priority_ = self.priority
            etree_.SubElement(element, 'priority').text = self.gds_format_float(priority_)
        if self.info is not None:
            info_ = self.info
            info_.to_etree(element, name_='info', mapping_=mapping_, reverse_mapping_=reverse_mapping_, nsmap_=nsmap_)
        if mapping_ is not None:
            mapping_[id(self)] = element
        if reverse_mapping_ is not None:
            reverse_mapping_[element] = self
        return element
    def build(self, node, gds_collector_=None):
        self.gds_collector_ = gds_collector_
        if SaveElementTreeNode:
            self.gds_elementtree_node_ = node
        already_processed = set()
        self.ns_prefix_ = node.prefix
        self._buildAttributes(node, node.attrib, already_processed)
        for child in node:
            nodeName_ = Tag_pattern_.match(child.tag).groups()[-1]
            self._buildChildren(child, node, nodeName_, gds_collector_=gds_collector_)
        return self
    def _buildAttributes(self, node, attrs, already_processed):
        super(weird_agentType, self)._buildAttributes(node, attrs, already_processed)
    def _buildChildren(self, child_, node, nodeName_, fromsubclass_=False, gds_collector_=None):
        if nodeName_ == 'firstname':
            value_ = child_.text
            value_ = self.gds_parse_string(value_, node, 'firstname')
            value_ = self.gds_validate_string(value_, node, 'firstname')
            self.firstname = value_
            self.firstname_nsprefix_ = child_.prefix
        elif nodeName_ == 'lastname':
            value_ = child_.text
            value_ = self.gds_parse_string(value_, node, 'lastname')
            value_ = self.gds_validate_string(value_, node, 'lastname')
            self.lastname = value_
            self.lastname_nsprefix_ = child_.prefix
        elif nodeName_ == 'priority' and child_.text:
            sval_ = child_.text
            fval_ = self.gds_parse_float(sval_, node, 'priority')
            fval_ = self.gds_validate_float(fval_, node, 'priority')
            self.priority = fval_
            self.priority_nsprefix_ = child_.prefix
        elif nodeName_ == 'info':
            obj_ = infoType.factory(parent_object_=self)
            obj_.build(child_, gds_collector_=gds_collector_)
            self.info = obj_
            obj_.original_tagname_ = 'info'
        super(weird_agentType, self)._buildChildren(child_, node, nodeName_, True)
# end class weird_agentType


class boosterType(GeneratedsSuper):
    __hash__ = GeneratedsSuper.__hash__
    member_data_items_ = [
        MemberSpec_('member_id', 'xs:string', 0, 1, {'use': 'optional', 'name': 'member-id'}),
        MemberSpec_('firstname', 'xs:string', 0, 0, {'name': 'firstname', 'type': 'xs:string'}, None),
        MemberSpec_('lastname', 'xs:string', 0, 0, {'name': 'lastname', 'type': 'xs:string'}, None),
        MemberSpec_('other_name', 'xs:float', 0, 0, {'name': 'other-name', 'type': 'xs:float'}, None),
        MemberSpec_('class_', 'xs:float', 0, 0, {'name': 'class', 'type': 'xs:float'}, None),
        MemberSpec_('other_value', 'xs:float', 1, 0, {'maxOccurs': 'unbounded', 'name': 'other-value', 'type': 'xs:float'}, None),
        MemberSpec_('type_', 'xs:float', 1, 0, {'maxOccurs': 'unbounded', 'name': 'type', 'type': 'xs:float'}, None),
        MemberSpec_('client_handler', 'client-handlerType', 1, 0, {'maxOccurs': 'unbounded', 'name': 'client-handler', 'type': 'client-handlerType'}, None),
    ]
    subclass = None
    superclass = None
    def __init__(self, member_id=None, firstname=None, lastname=None, other_name=None, class_=None, other_value=None, type_=None, client_handler=None, gds_collector_=None, **kwargs_):
        self.gds_collector_ = gds_collector_
        self.gds_elementtree_node_ = None
        self.original_tagname_ = None
        self.parent_object_ = kwargs_.get('parent_object_')
        self.ns_prefix_ = None
        self.member_id = _cast(None, member_id)
        self.member_id_nsprefix_ = None
        self.firstname = firstname
        self.firstname_nsprefix_ = None
        self.lastname = lastname
        self.lastname_nsprefix_ = None
        self.other_name = other_name
        self.other_name_nsprefix_ = None
        self.class_ = class_
        self.class__nsprefix_ = None
        if other_value is None:
            self.other_value = []
        else:
            self.other_value = other_value
        self.other_value_nsprefix_ = None
        if type_ is None:
            self.type_ = []
        else:
            self.type_ = type_
        self.type__nsprefix_ = None
        if client_handler is None:
            self.client_handler = []
        else:
            self.client_handler = client_handler
        self.client_handler_nsprefix_ = None
    def factory(*args_, **kwargs_):
        if CurrentSubclassModule_ is not None:
            subclass = getSubclassFromModule_(
                CurrentSubclassModule_, boosterType)
            if subclass is not None:
                return subclass(*args_, **kwargs_)
        if boosterType.subclass:
            return boosterType.subclass(*args_, **kwargs_)
        else:
            return boosterType(*args_, **kwargs_)
    factory = staticmethod(factory)
    def get_ns_prefix_(self):
        return self.ns_prefix_
    def set_ns_prefix_(self, ns_prefix):
        self.ns_prefix_ = ns_prefix
    def get_firstname(self):
        return self.firstname
    def set_firstname(self, firstname):
        self.firstname = firstname
    def get_lastname(self):
        return self.lastname
    def set_lastname(self, lastname):
        self.lastname = lastname
    def get_other_name(self):
        return self.other_name
    def set_other_name(self, other_name):
        self.other_name = other_name
    def get_class(self):
        return self.class_
    def set_class(self, class_):
        self.class_ = class_
    def get_other_value(self):
        return self.other_value
    def set_other_value(self, other_value):
        self.other_value = other_value
    def add_other_value(self, value):
        self.other_value.append(value)
    def insert_other_value_at(self, index, value):
        self.other_value.insert(index, value)
    def replace_other_value_at(self, index, value):
        self.other_value[index] = value
    def get_type(self):
        return self.type_
    def set_type(self, type_):
        self.type_ = type_
    def add_type(self, value):
        self.type_.append(value)
    def insert_type_at(self, index, value):
        self.type_.insert(index, value)
    def replace_type_at(self, index, value):
        self.type_[index] = value
    def get_client_handler(self):
        return self.client_handler
    def set_client_handler(self, client_handler):
        self.client_handler = client_handler
    def add_client_handler(self, value):
        self.client_handler.append(value)
    def insert_client_handler_at(self, index, value):
        self.client_handler.insert(index, value)
    def replace_client_handler_at(self, index, value):
        self.client_handler[index] = value
    def get_member_id(self):
        return self.member_id
    def set_member_id(self, member_id):
        self.member_id = member_id
    def _hasContent(self):
        if (
            self.firstname is not None or
            self.lastname is not None or
            self.other_name is not None or
            self.class_ is not None or
            self.other_value or
            self.type_ or
            self.client_handler
        ):
            return True
        else:
            return False
    def to_etree(self, parent_element=None, name_='boosterType', mapping_=None, reverse_mapping_=None, nsmap_=None):
        if parent_element is None:
            element = etree_.Element(name_, nsmap=nsmap_)
        else:
            element = etree_.SubElement(parent_element, name_, nsmap=nsmap_)
        if self.member_id is not None:
            element.set('member-id', self.gds_format_string(self.member_id))
        if self.firstname is not None:
            firstname_ = self.firstname
            etree_.SubElement(element, 'firstname').text = self.gds_format_string(firstname_)
        if self.lastname is not None:
            lastname_ = self.lastname
            etree_.SubElement(element, 'lastname').text = self.gds_format_string(lastname_)
        if self.other_name is not None:
            other_name_ = self.other_name
            etree_.SubElement(element, 'other-name').text = self.gds_format_float(other_name_)
        if self.class_ is not None:
            class__ = self.class_
            etree_.SubElement(element, 'class').text = self.gds_format_float(class__)
        for other_value_ in self.other_value:
            etree_.SubElement(element, 'other-value').text = self.gds_format_float(other_value_)
        for type__ in self.type_:
            etree_.SubElement(element, 'type').text = self.gds_format_float(type__)
        for client_handler_ in self.client_handler:
            client_handler_.to_etree(element, name_='client-handler', mapping_=mapping_, reverse_mapping_=reverse_mapping_, nsmap_=nsmap_)
        if mapping_ is not None:
            mapping_[id(self)] = element
        if reverse_mapping_ is not None:
            reverse_mapping_[element] = self
        return element
    def build(self, node, gds_collector_=None):
        self.gds_collector_ = gds_collector_
        if SaveElementTreeNode:
            self.gds_elementtree_node_ = node
        already_processed = set()
        self.ns_prefix_ = node.prefix
        self._buildAttributes(node, node.attrib, already_processed)
        for child in node:
            nodeName_ = Tag_pattern_.match(child.tag).groups()[-1]
            self._buildChildren(child, node, nodeName_, gds_collector_=gds_collector_)
        return self
    def _buildAttributes(self, node, attrs, already_processed):
        value = find_attr_value_('member-id', node)
        if value is not None and 'member-id' not in already_processed:
            already_processed.add('member-id')
            self.member_id = value
    def _buildChildren(self, child_, node, nodeName_, fromsubclass_=False, gds_collector_=None):
        if nodeName_ == 'firstname':
            value_ = child_.text
            value_ = self.gds_parse_string(value_, node, 'firstname')
            value_ = self.gds_validate_string(value_, node, 'firstname')
            self.firstname = value_
            self.firstname_nsprefix_ = child_.prefix
        elif nodeName_ == 'lastname':
            value_ = child_.text
            value_ = self.gds_parse_string(value_, node, 'lastname')
            value_ = self.gds_validate_string(value_, node, 'lastname')
            self.lastname = value_
            self.lastname_nsprefix_ = child_.prefix
        elif nodeName_ == 'other-name' and child_.text:
            sval_ = child_.text
            fval_ = self.gds_parse_float(sval_, node, 'other_name')
            fval_ = self.gds_validate_float(fval_, node, 'other_name')
            self.other_name = fval_
            self.other_name_nsprefix_ = child_.prefix
        elif nodeName_ == 'class' and child_.text:
            sval_ = child_.text
            fval_ = self.gds_parse_float(sval_, node, 'class')
            fval_ = self.gds_validate_float(fval_, node, 'class')
            self.class_ = fval_
            self.class_nsprefix_ = child_.prefix
        elif nodeName_ == 'other-value' and child_.text:
            sval_ = child_.text
            fval_ = self.gds_parse_float(sval_, node, 'other_value')
            fval_ = self.gds_validate_float(fval_, node, 'other_value')
            self.other_value.append(fval_)
            self.other_value_nsprefix_ = child_.prefix
        elif nodeName_ == 'type' and child_.text:
            sval_ = child_.text
            fval_ = self.gds_parse_float(sval_, node, 'type')
            fval_ = self.gds_validate_float(fval_, node, 'type')
            self.type_.append(fval_)
            self.type_nsprefix_ = child_.prefix
        elif nodeName_ == 'client-handler':
            obj_ = client_handlerType.factory(parent_object_=self)
            obj_.build(child_, gds_collector_=gds_collector_)
            self.client_handler.append(obj_)
            obj_.original_tagname_ = 'client-handler'
# end class boosterType


class infoType(GeneratedsSuper):
    __hash__ = GeneratedsSuper.__hash__
    member_data_items_ = [
        MemberSpec_('name', 'xs:string', 0, 1, {'use': 'optional', 'name': 'name'}),
        MemberSpec_('type_', 'xs:integer', 0, 1, {'use': 'optional', 'name': 'type_'}),
        MemberSpec_('rating', 'xs:float', 0, 1, {'use': 'optional', 'name': 'rating'}),
    ]
    subclass = None
    superclass = None
    def __init__(self, name=None, type_=None, rating=None, gds_collector_=None, **kwargs_):
        self.gds_collector_ = gds_collector_
        self.gds_elementtree_node_ = None
        self.original_tagname_ = None
        self.parent_object_ = kwargs_.get('parent_object_')
        self.ns_prefix_ = None
        self.name = _cast(None, name)
        self.name_nsprefix_ = None
        self.type_ = _cast(int, type_)
        self.type__nsprefix_ = None
        self.rating = _cast(float, rating)
        self.rating_nsprefix_ = None
    def factory(*args_, **kwargs_):
        if CurrentSubclassModule_ is not None:
            subclass = getSubclassFromModule_(
                CurrentSubclassModule_, infoType)
            if subclass is not None:
                return subclass(*args_, **kwargs_)
        if infoType.subclass:
            return infoType.subclass(*args_, **kwargs_)
        else:
            return infoType(*args_, **kwargs_)
    factory = staticmethod(factory)
    def get_ns_prefix_(self):
        return self.ns_prefix_
    def set_ns_prefix_(self, ns_prefix):
        self.ns_prefix_ = ns_prefix
    def get_name(self):
        return self.name
    def set_name(self, name):
        self.name = name
    def get_type(self):
        return self.type_
    def set_type(self, type_):
        self.type_ = type_
    def get_rating(self):
        return self.rating
    def set_rating(self, rating):
        self.rating = rating
    def _hasContent(self):
        if (

        ):
            return True
        else:
            return False
    def to_etree(self, parent_element=None, name_='infoType', mapping_=None, reverse_mapping_=None, nsmap_=None):
        if parent_element is None:
            element = etree_.Element(name_, nsmap=nsmap_)
        else:
            element = etree_.SubElement(parent_element, name_, nsmap=nsmap_)
        if self.name is not None:
            element.set('name', self.gds_format_string(self.name))
        if self.type_ is not None:
            element.set('type', self.gds_format_integer(self.type_))
        if self.rating is not None:
            element.set('rating', self.gds_format_float(self.rating))
        if mapping_ is not None:
            mapping_[id(self)] = element
        if reverse_mapping_ is not None:
            reverse_mapping_[element] = self
        return element
    def build(self, node, gds_collector_=None):
        self.gds_collector_ = gds_collector_
        if SaveElementTreeNode:
            self.gds_elementtree_node_ = node
        already_processed = set()
        self.ns_prefix_ = node.prefix
        self._buildAttributes(node, node.attrib, already_processed)
        for child in node:
            nodeName_ = Tag_pattern_.match(child.tag).groups()[-1]
            self._buildChildren(child, node, nodeName_, gds_collector_=gds_collector_)
        return self
    def _buildAttributes(self, node, attrs, already_processed):
        value = find_attr_value_('name', node)
        if value is not None and 'name' not in already_processed:
            already_processed.add('name')
            self.name = value
        value = find_attr_value_('type', node)
        if value is not None and 'type' not in already_processed:
            already_processed.add('type')
            self.type_ = self.gds_parse_integer(value, node, 'type')
        value = find_attr_value_('rating', node)
        if value is not None and 'rating' not in already_processed:
            already_processed.add('rating')
            value = self.gds_parse_float(value, node, 'rating')
            self.rating = value
    def _buildChildren(self, child_, node, nodeName_, fromsubclass_=False, gds_collector_=None):
        pass
# end class infoType


class vehicleType(GeneratedsSuper):
    __hash__ = GeneratedsSuper.__hash__
    member_data_items_ = [
        MemberSpec_('wheelcount', 'xs:integer', 0, 0, {'name': 'wheelcount', 'type': 'xs:integer'}, None),
    ]
    subclass = None
    superclass = None
    def __init__(self, wheelcount=None, extensiontype_=None, gds_collector_=None, **kwargs_):
        self.gds_collector_ = gds_collector_
        self.gds_elementtree_node_ = None
        self.original_tagname_ = None
        self.parent_object_ = kwargs_.get('parent_object_')
        self.ns_prefix_ = None
        self.wheelcount = wheelcount
        self.wheelcount_nsprefix_ = None
        self.extensiontype_ = extensiontype_
    def factory(*args_, **kwargs_):
        if CurrentSubclassModule_ is not None:
            subclass = getSubclassFromModule_(
                CurrentSubclassModule_, vehicleType)
            if subclass is not None:
                return subclass(*args_, **kwargs_)
        if vehicleType.subclass:
            return vehicleType.subclass(*args_, **kwargs_)
        else:
            return vehicleType(*args_, **kwargs_)
    factory = staticmethod(factory)
    def get_ns_prefix_(self):
        return self.ns_prefix_
    def set_ns_prefix_(self, ns_prefix):
        self.ns_prefix_ = ns_prefix
    def get_wheelcount(self):
        return self.wheelcount
    def set_wheelcount(self, wheelcount):
        self.wheelcount = wheelcount
    def get_extensiontype_(self): return self.extensiontype_
    def set_extensiontype_(self, extensiontype_): self.extensiontype_ = extensiontype_
    def _hasContent(self):
        if (
            self.wheelcount is not None
        ):
            return True
        else:
            return False
    def to_etree(self, parent_element=None, name_='vehicleType', mapping_=None, reverse_mapping_=None, nsmap_=None):
        if parent_element is None:
            element = etree_.Element(name_, nsmap=nsmap_)
        else:
            element = etree_.SubElement(parent_element, name_, nsmap=nsmap_)
        if self.extensiontype_ is not None:
            element.set('{http://www.w3.org/2001/XMLSchema-instance}type', self.extensiontype_)
        if self.wheelcount is not None:
            wheelcount_ = self.wheelcount
            etree_.SubElement(element, 'wheelcount').text = self.gds_format_integer(wheelcount_)
        if mapping_ is not None:
            mapping_[id(self)] = element
        if reverse_mapping_ is not None:
            reverse_mapping_[element] = self
        return element
    def build(self, node, gds_collector_=None):
        self.gds_collector_ = gds_collector_
        if SaveElementTreeNode:
            self.gds_elementtree_node_ = node
        already_processed = set()
        self.ns_prefix_ = node.prefix
        self._buildAttributes(node, node.attrib, already_processed)
        for child in node:
            nodeName_ = Tag_pattern_.match(child.tag).groups()[-1]
            self._buildChildren(child, node, nodeName_, gds_collector_=gds_collector_)
        return self
    def _buildAttributes(self, node, attrs, already_processed):
        value = find_attr_value_('xsi:type', node)
        if value is not None and 'xsi:type' not in already_processed:
            already_processed.add('xsi:type')
            self.extensiontype_ = value
    def _buildChildren(self, child_, node, nodeName_, fromsubclass_=False, gds_collector_=None):
        if nodeName_ == 'wheelcount' and child_.text:
            sval_ = child_.text
            ival_ = self.gds_parse_integer(sval_, node, 'wheelcount')
            ival_ = self.gds_validate_integer(ival_, node, 'wheelcount')
            self.wheelcount = ival_
            self.wheelcount_nsprefix_ = child_.prefix
# end class vehicleType


class automobile(vehicleType):
    __hash__ = GeneratedsSuper.__hash__
    member_data_items_ = [
        MemberSpec_('drivername', 'xs:string', 0, 0, {'name': 'drivername', 'type': 'xs:string'}, None),
    ]
    subclass = None
    superclass = vehicleType
    def __init__(self, wheelcount=None, drivername=None, gds_collector_=None, **kwargs_):
        self.gds_collector_ = gds_collector_
        self.gds_elementtree_node_ = None
        self.original_tagname_ = None
        self.parent_object_ = kwargs_.get('parent_object_')
        self.ns_prefix_ = None
        super(globals().get("automobile"), self).__init__(wheelcount,  **kwargs_)
        self.drivername = drivername
        self.drivername_nsprefix_ = None
    def factory(*args_, **kwargs_):
        if CurrentSubclassModule_ is not None:
            subclass = getSubclassFromModule_(
                CurrentSubclassModule_, automobile)
            if subclass is not None:
                return subclass(*args_, **kwargs_)
        if automobile.subclass:
            return automobile.subclass(*args_, **kwargs_)
        else:
            return automobile(*args_, **kwargs_)
    factory = staticmethod(factory)
    def get_ns_prefix_(self):
        return self.ns_prefix_
    def set_ns_prefix_(self, ns_prefix):
        self.ns_prefix_ = ns_prefix
    def get_drivername(self):
        return self.drivername
    def set_drivername(self, drivername):
        self.drivername = drivername
    def _hasContent(self):
        if (
            self.drivername is not None or
            super(automobile, self)._hasContent()
        ):
            return True
        else:
            return False
    def to_etree(self, parent_element=None, name_='automobile', mapping_=None, reverse_mapping_=None, nsmap_=None):
        element = super(automobile, self).to_etree(parent_element, name_, mapping_, reverse_mapping_, nsmap_)
        if self.drivername is not None:
            drivername_ = self.drivername
            etree_.SubElement(element, 'drivername').text = self.gds_format_string(drivername_)
        if mapping_ is not None:
            mapping_[id(self)] = element
        if reverse_mapping_ is not None:
            reverse_mapping_[element] = self
        return element
    def build(self, node, gds_collector_=None):
        self.gds_collector_ = gds_collector_
        if SaveElementTreeNode:
            self.gds_elementtree_node_ = node
        already_processed = set()
        self.ns_prefix_ = node.prefix
        self._buildAttributes(node, node.attrib, already_processed)
        for child in node:
            nodeName_ = Tag_pattern_.match(child.tag).groups()[-1]
            self._buildChildren(child, node, nodeName_, gds_collector_=gds_collector_)
        return self
    def _buildAttributes(self, node, attrs, already_processed):
        super(automobile, self)._buildAttributes(node, attrs, already_processed)
    def _buildChildren(self, child_, node, nodeName_, fromsubclass_=False, gds_collector_=None):
        if nodeName_ == 'drivername':
            value_ = child_.text
            value_ = self.gds_parse_string(value_, node, 'drivername')
            value_ = self.gds_validate_string(value_, node, 'drivername')
            self.drivername = value_
            self.drivername_nsprefix_ = child_.prefix
        super(automobile, self)._buildChildren(child_, node, nodeName_, True)
# end class automobile


class airplane(vehicleType):
    __hash__ = GeneratedsSuper.__hash__
    member_data_items_ = [
        MemberSpec_('pilotname', 'xs:string', 0, 0, {'name': 'pilotname', 'type': 'xs:string'}, None),
    ]
    subclass = None
    superclass = vehicleType
    def __init__(self, wheelcount=None, pilotname=None, gds_collector_=None, **kwargs_):
        self.gds_collector_ = gds_collector_
        self.gds_elementtree_node_ = None
        self.original_tagname_ = None
        self.parent_object_ = kwargs_.get('parent_object_')
        self.ns_prefix_ = None
        super(globals().get("airplane"), self).__init__(wheelcount,  **kwargs_)
        self.pilotname = pilotname
        self.pilotname_nsprefix_ = None
    def factory(*args_, **kwargs_):
        if CurrentSubclassModule_ is not None:
            subclass = getSubclassFromModule_(
                CurrentSubclassModule_, airplane)
            if subclass is not None:
                return subclass(*args_, **kwargs_)
        if airplane.subclass:
            return airplane.subclass(*args_, **kwargs_)
        else:
            return airplane(*args_, **kwargs_)
    factory = staticmethod(factory)
    def get_ns_prefix_(self):
        return self.ns_prefix_
    def set_ns_prefix_(self, ns_prefix):
        self.ns_prefix_ = ns_prefix
    def get_pilotname(self):
        return self.pilotname
    def set_pilotname(self, pilotname):
        self.pilotname = pilotname
    def _hasContent(self):
        if (
            self.pilotname is not None or
            super(airplane, self)._hasContent()
        ):
            return True
        else:
            return False
    def to_etree(self, parent_element=None, name_='airplane', mapping_=None, reverse_mapping_=None, nsmap_=None):
        element = super(airplane, self).to_etree(parent_element, name_, mapping_, reverse_mapping_, nsmap_)
        if self.pilotname is not None:
            pilotname_ = self.pilotname
            etree_.SubElement(element, 'pilotname').text = self.gds_format_string(pilotname_)
        if mapping_ is not None:
            mapping_[id(self)] = element
        if reverse_mapping_ is not None:
            reverse_mapping_[element] = self
        return element
    def build(self, node, gds_collector_=None):
        self.gds_collector_ = gds_collector_
        if SaveElementTreeNode:
            self.gds_elementtree_node_ = node
        already_processed = set()
        self.ns_prefix_ = node.prefix
        self._buildAttributes(node, node.attrib, already_processed)
        for child in node:
            nodeName_ = Tag_pattern_.match(child.tag).groups()[-1]
            self._buildChildren(child, node, nodeName_, gds_collector_=gds_collector_)
        return self
    def _buildAttributes(self, node, attrs, already_processed):
        super(airplane, self)._buildAttributes(node, attrs, already_processed)
    def _buildChildren(self, child_, node, nodeName_, fromsubclass_=False, gds_collector_=None):
        if nodeName_ == 'pilotname':
            value_ = child_.text
            value_ = self.gds_parse_string(value_, node, 'pilotname')
            value_ = self.gds_validate_string(value_, node, 'pilotname')
            self.pilotname = value_
            self.pilotname_nsprefix_ = child_.prefix
        super(airplane, self)._buildChildren(child_, node, nodeName_, True)
# end class airplane


class hot_agent(GeneratedsSuper):
    __hash__ = GeneratedsSuper.__hash__
    member_data_items_ = [
        MemberSpec_('firstname', 'xs:string', 0, 0, {'default': 'empty\\name', 'name': 'firstname', 'type': 'xs:string'}, None),
        MemberSpec_('lastname', 'xs:string', 0, 0, {'default': "no 'last' name", 'name': 'lastname', 'type': 'xs:string'}, None),
        MemberSpec_('priority', 'xs:float', 0, 0, {'name': 'priority', 'type': 'xs:float'}, None),
        MemberSpec_('startDate', 'xs:date', 0, 0, {'name': 'startDate', 'type': 'xs:date'}, None),
    ]
    subclass = None
    superclass = None
    def __init__(self, firstname='empty\\name', lastname='no \'last\' name', priority=None, startDate=None, gds_collector_=None, **kwargs_):
        self.gds_collector_ = gds_collector_
        self.gds_elementtree_node_ = None
        self.original_tagname_ = None
        self.parent_object_ = kwargs_.get('parent_object_')
        self.ns_prefix_ = None
        self.firstname = firstname
        self.firstname_nsprefix_ = None
        self.lastname = lastname
        self.lastname_nsprefix_ = None
        self.priority = priority
        self.priority_nsprefix_ = None
        if isinstance(startDate, BaseStrType_):
            initvalue_ = datetime_.datetime.strptime(startDate, '%Y-%m-%d').date()
        else:
            initvalue_ = startDate
        self.startDate = initvalue_
        self.startDate_nsprefix_ = None
        self.anyAttributes_ = {}
    def factory(*args_, **kwargs_):
        if CurrentSubclassModule_ is not None:
            subclass = getSubclassFromModule_(
                CurrentSubclassModule_, hot_agent)
            if subclass is not None:
                return subclass(*args_, **kwargs_)
        if hot_agent.subclass:
            return hot_agent.subclass(*args_, **kwargs_)
        else:
            return hot_agent(*args_, **kwargs_)
    factory = staticmethod(factory)
    def get_ns_prefix_(self):
        return self.ns_prefix_
    def set_ns_prefix_(self, ns_prefix):
        self.ns_prefix_ = ns_prefix
    def get_firstname(self):
        return self.firstname
    def set_firstname(self, firstname):
        self.firstname = firstname
    def get_lastname(self):
        return self.lastname
    def set_lastname(self, lastname):
        self.lastname = lastname
    def get_priority(self):
        return self.priority
    def set_priority(self, priority):
        self.priority = priority
    def get_startDate(self):
        return self.startDate
    def set_startDate(self, startDate):
        self.startDate = startDate
    def get_anyAttributes_(self): return self.anyAttributes_
    def set_anyAttributes_(self, anyAttributes_): self.anyAttributes_ = anyAttributes_
    def _hasContent(self):
        if (
            self.firstname != "empty\name" or
            self.lastname != "no 'last' name" or
            self.priority is not None or
            self.startDate is not None
        ):
            return True
        else:
            return False
    def to_etree(self, parent_element=None, name_='hot.agent', mapping_=None, reverse_mapping_=None, nsmap_=None):
        if parent_element is None:
            element = etree_.Element(name_, nsmap=nsmap_)
        else:
            element = etree_.SubElement(parent_element, name_, nsmap=nsmap_)
        if self.firstname is not None:
            firstname_ = self.firstname
            etree_.SubElement(element, 'firstname').text = self.gds_format_string(firstname_)
        if self.lastname is not None:
            lastname_ = self.lastname
            etree_.SubElement(element, 'lastname').text = self.gds_format_string(lastname_)
        if self.priority is not None:
            priority_ = self.priority
            etree_.SubElement(element, 'priority').text = self.gds_format_float(priority_)
        if self.startDate is not None:
            startDate_ = self.startDate
            etree_.SubElement(element, 'startDate').text = self.gds_format_date(startDate_)
        if mapping_ is not None:
            mapping_[id(self)] = element
        if reverse_mapping_ is not None:
            reverse_mapping_[element] = self
        return element
    def build(self, node, gds_collector_=None):
        self.gds_collector_ = gds_collector_
        if SaveElementTreeNode:
            self.gds_elementtree_node_ = node
        already_processed = set()
        self.ns_prefix_ = node.prefix
        self._buildAttributes(node, node.attrib, already_processed)
        for child in node:
            nodeName_ = Tag_pattern_.match(child.tag).groups()[-1]
            self._buildChildren(child, node, nodeName_, gds_collector_=gds_collector_)
        return self
    def _buildAttributes(self, node, attrs, already_processed):
        self.anyAttributes_ = {}
        for name, value in attrs.items():
            if name not in already_processed:
                self.anyAttributes_[name] = value
    def _buildChildren(self, child_, node, nodeName_, fromsubclass_=False, gds_collector_=None):
        if nodeName_ == 'firstname':
            value_ = child_.text
            value_ = self.gds_parse_string(value_, node, 'firstname')
            value_ = self.gds_validate_string(value_, node, 'firstname')
            self.firstname = value_
            self.firstname_nsprefix_ = child_.prefix
        elif nodeName_ == 'lastname':
            value_ = child_.text
            value_ = self.gds_parse_string(value_, node, 'lastname')
            value_ = self.gds_validate_string(value_, node, 'lastname')
            self.lastname = value_
            self.lastname_nsprefix_ = child_.prefix
        elif nodeName_ == 'priority' and child_.text:
            sval_ = child_.text
            fval_ = self.gds_parse_float(sval_, node, 'priority')
            fval_ = self.gds_validate_float(fval_, node, 'priority')
            self.priority = fval_
            self.priority_nsprefix_ = child_.prefix
        elif nodeName_ == 'startDate':
            sval_ = child_.text
            dval_ = self.gds_parse_date(sval_)
            self.startDate = dval_
            self.startDate_nsprefix_ = child_.prefix
# end class hot_agent


class client_handlerType(GeneratedsSuper):
    __hash__ = GeneratedsSuper.__hash__
    member_data_items_ = [
        MemberSpec_('fullname', 'xs:string', 0, 0, {'name': 'fullname', 'type': 'xs:string'}, None),
        MemberSpec_('refid', 'xs:integer', 0, 0, {'name': 'refid', 'type': 'xs:integer'}, None),
    ]
    subclass = None
    superclass = None
    def __init__(self, fullname=None, refid=None, gds_collector_=None, **kwargs_):
        self.gds_collector_ = gds_collector_
        self.gds_elementtree_node_ = None
        self.original_tagname_ = None
        self.parent_object_ = kwargs_.get('parent_object_')
        self.ns_prefix_ = None
        self.fullname = fullname
        self.fullname_nsprefix_ = None
        self.refid = refid
        self.refid_nsprefix_ = None
    def factory(*args_, **kwargs_):
        if CurrentSubclassModule_ is not None:
            subclass = getSubclassFromModule_(
                CurrentSubclassModule_, client_handlerType)
            if subclass is not None:
                return subclass(*args_, **kwargs_)
        if client_handlerType.subclass:
            return client_handlerType.subclass(*args_, **kwargs_)
        else:
            return client_handlerType(*args_, **kwargs_)
    factory = staticmethod(factory)
    def get_ns_prefix_(self):
        return self.ns_prefix_
    def set_ns_prefix_(self, ns_prefix):
        self.ns_prefix_ = ns_prefix
    def get_fullname(self):
        return self.fullname
    def set_fullname(self, fullname):
        self.fullname = fullname
    def get_refid(self):
        return self.refid
    def set_refid(self, refid):
        self.refid = refid
    def _hasContent(self):
        if (
            self.fullname is not None or
            self.refid is not None
        ):
            return True
        else:
            return False
    def to_etree(self, parent_element=None, name_='client-handlerType', mapping_=None, reverse_mapping_=None, nsmap_=None):
        if parent_element is None:
            element = etree_.Element(name_, nsmap=nsmap_)
        else:
            element = etree_.SubElement(parent_element, name_, nsmap=nsmap_)
        if self.fullname is not None:
            fullname_ = self.fullname
            etree_.SubElement(element, 'fullname').text = self.gds_format_string(fullname_)
        if self.refid is not None:
            refid_ = self.refid
            etree_.SubElement(element, 'refid').text = self.gds_format_integer(refid_)
        if mapping_ is not None:
            mapping_[id(self)] = element
        if reverse_mapping_ is not None:
            reverse_mapping_[element] = self
        return element
    def build(self, node, gds_collector_=None):
        self.gds_collector_ = gds_collector_
        if SaveElementTreeNode:
            self.gds_elementtree_node_ = node
        already_processed = set()
        self.ns_prefix_ = node.prefix
        self._buildAttributes(node, node.attrib, already_processed)
        for child in node:
            nodeName_ = Tag_pattern_.match(child.tag).groups()[-1]
            self._buildChildren(child, node, nodeName_, gds_collector_=gds_collector_)
        return self
    def _buildAttributes(self, node, attrs, already_processed):
        pass
    def _buildChildren(self, child_, node, nodeName_, fromsubclass_=False, gds_collector_=None):
        if nodeName_ == 'fullname':
            value_ = child_.text
            value_ = self.gds_parse_string(value_, node, 'fullname')
            value_ = self.gds_validate_string(value_, node, 'fullname')
            self.fullname = value_
            self.fullname_nsprefix_ = child_.prefix
        elif nodeName_ == 'refid' and child_.text:
            sval_ = child_.text
            ival_ = self.gds_parse_integer(sval_, node, 'refid')
            ival_ = self.gds_validate_integer(ival_, node, 'refid')
            self.refid = ival_
            self.refid_nsprefix_ = child_.prefix
# end class client_handlerType


GDSClassesMapping = {
    'agent': agentType,
    'booster': boosterType,
    'comments': commentsType,
    'info': infoType,
    'java-programmer': java_programmerType,
    'param': paramType,
    'people': peopleType,
    'person': personType,
    'programmer': programmerType,
    'python-programmer': python_programmerType,
    'special-agent': special_agentType,
    'vehicle': vehicleType,
    'weird-agent': weird_agentType,
}


USAGE_TEXT = """
Usage: python <Parser>.py [ -s ] <in_xml_file>
"""


def usage():
    print(USAGE_TEXT)
    sys.exit(1)


def get_root_tag(node):
    tag = Tag_pattern_.match(node.tag).groups()[-1]
    rootClass = GDSClassesMapping.get(tag)
    if rootClass is None:
        rootClass = globals().get(tag)
    return tag, rootClass


def get_required_ns_prefix_defs(rootNode):
    '''Get all name space prefix definitions required in this XML doc.
    Return a dictionary of definitions and a char string of definitions.
    '''
    nsmap = {
        prefix: uri
        for node in rootNode.iter()
        for (prefix, uri) in node.nsmap.items()
        if prefix is not None
    }
    namespacedefs = ' '.join([
        'xmlns:{}="{}"'.format(prefix, uri)
        for prefix, uri in nsmap.items()
    ])
    return nsmap, namespacedefs


def parse(inFileName, silence=False, print_warnings=True):
    global CapturedNsmap_
    gds_collector = GdsCollector_()
    parser = None
    doc = parsexml_(inFileName, parser)
    rootNode = doc.getroot()
    rootTag, rootClass = get_root_tag(rootNode)
    if rootClass is None:
        rootTag = 'peopleType'
        rootClass = peopleType
    rootObj = rootClass.factory()
    rootObj.build(rootNode, gds_collector_=gds_collector)
    CapturedNsmap_, namespacedefs = get_required_ns_prefix_defs(rootNode)
    if not SaveElementTreeNode:
        doc = None
        rootNode = None
##     if not silence:
##         sys.stdout.write('<?xml version="1.0" ?>\n')
##         rootObj.export(
##             sys.stdout, 0, name_=rootTag,
##             namespacedef_=namespacedefs,
##             pretty_print=True)
    if print_warnings and len(gds_collector.get_messages()) > 0:
        separator = ('-' * 50) + '\n'
        sys.stderr.write(separator)
        sys.stderr.write('----- Warnings -- count: {} -----\n'.format(
            len(gds_collector.get_messages()), ))
        gds_collector.write_messages(sys.stderr)
        sys.stderr.write(separator)
    return rootObj


def parseEtree(inFileName, silence=False, print_warnings=True,
               mapping=None, reverse_mapping=None, nsmap=None):
    parser = None
    doc = parsexml_(inFileName, parser)
    gds_collector = GdsCollector_()
    rootNode = doc.getroot()
    rootTag, rootClass = get_root_tag(rootNode)
    if rootClass is None:
        rootTag = 'peopleType'
        rootClass = peopleType
    rootObj = rootClass.factory()
    rootObj.build(rootNode, gds_collector_=gds_collector)
    if mapping is None:
        mapping = {}
    if reverse_mapping is None:
        reverse_mapping = {}
    rootElement = rootObj.to_etree(
        None, name_=rootTag, mapping_=mapping,
        reverse_mapping_=reverse_mapping, nsmap_=nsmap)
    reverse_node_mapping = rootObj.gds_reverse_node_mapping(mapping)
    # Enable Python to collect the space used by the DOM.
    if not SaveElementTreeNode:
        doc = None
        rootNode = None
##     if not silence:
##         content = etree_.tostring(
##             rootElement, pretty_print=True,
##             xml_declaration=True, encoding="utf-8")
##         sys.stdout.write(str(content))
##         sys.stdout.write('\n')
    if print_warnings and len(gds_collector.get_messages()) > 0:
        separator = ('-' * 50) + '\n'
        sys.stderr.write(separator)
        sys.stderr.write('----- Warnings -- count: {} -----\n'.format(
            len(gds_collector.get_messages()), ))
        gds_collector.write_messages(sys.stderr)
        sys.stderr.write(separator)
    return rootObj, rootElement, mapping, reverse_node_mapping


def parseString(inString, silence=False, print_warnings=True):
    '''Parse a string, create the object tree, and export it.

    Arguments:
    - inString -- A string.  This XML fragment should not start
      with an XML declaration containing an encoding.
    - silence -- A boolean.  If False, export the object.
    Returns -- The root object in the tree.
    '''
    parser = None
    rootNode= parsexmlstring_(inString, parser)
    gds_collector = GdsCollector_()
    rootTag, rootClass = get_root_tag(rootNode)
    if rootClass is None:
        rootTag = 'peopleType'
        rootClass = peopleType
    rootObj = rootClass.factory()
    rootObj.build(rootNode, gds_collector_=gds_collector)
    if not SaveElementTreeNode:
        rootNode = None
##     if not silence:
##         sys.stdout.write('<?xml version="1.0" ?>\n')
##         rootObj.export(
##             sys.stdout, 0, name_=rootTag,
##             namespacedef_='')
    if print_warnings and len(gds_collector.get_messages()) > 0:
        separator = ('-' * 50) + '\n'
        sys.stderr.write(separator)
        sys.stderr.write('----- Warnings -- count: {} -----\n'.format(
            len(gds_collector.get_messages()), ))
        gds_collector.write_messages(sys.stderr)
        sys.stderr.write(separator)
    return rootObj


def parseLiteral(inFileName, silence=False, print_warnings=True):
    parser = None
    doc = parsexml_(inFileName, parser)
    gds_collector = GdsCollector_()
    rootNode = doc.getroot()
    rootTag, rootClass = get_root_tag(rootNode)
    if rootClass is None:
        rootTag = 'peopleType'
        rootClass = peopleType
    rootObj = rootClass.factory()
    rootObj.build(rootNode, gds_collector_=gds_collector)
    # Enable Python to collect the space used by the DOM.
    if not SaveElementTreeNode:
        doc = None
        rootNode = None
##     if not silence:
##         sys.stdout.write('#from to_etree2_sup import *\n\n')
##         sys.stdout.write('import to_etree2_sup as model_\n\n')
##         sys.stdout.write('rootObj = model_.rootClass(\n')
##         rootObj.exportLiteral(sys.stdout, 0, name_=rootTag)
##         sys.stdout.write(')\n')
    if print_warnings and len(gds_collector.get_messages()) > 0:
        separator = ('-' * 50) + '\n'
        sys.stderr.write(separator)
        sys.stderr.write('----- Warnings -- count: {} -----\n'.format(
            len(gds_collector.get_messages()), ))
        gds_collector.write_messages(sys.stderr)
        sys.stderr.write(separator)
    return rootObj


def main():
    args = sys.argv[1:]
    if len(args) == 1:
        parse(args[0])
    else:
        usage()


if __name__ == '__main__':
    #import pdb; pdb.set_trace()
    main()

RenameMappings_ = {
}

#
# Mapping of namespaces to types defined in them
# and the file in which each is defined.
# simpleTypes are marked "ST" and complexTypes "CT".
NamespaceToDefMappings_ = {}

__all__ = [
    "agentType",
    "airplane",
    "automobile",
    "boosterType",
    "client_handlerType",
    "commentsType",
    "hot_agent",
    "infoType",
    "java_programmerType",
    "paramType",
    "peopleType",
    "personType",
    "programmerType",
    "python_programmerType",
    "special_agentType",
    "specialperson",
    "vehicleType",
    "weird_agentType"
]
