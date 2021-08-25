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
#   ('-o', 'tests/simpletypes_other2_sup.py')
#   ('-s', 'tests/simpletypes_other2_sub.py')
#   ('--super', 'simpletypes_other2_sup')
#
# Command line arguments:
#   tests/simpletypes_other.xsd
#
# Command line:
#   generateDS.py --no-dates --no-versions --silence --member-specs="list" -f -o "tests/simpletypes_other2_sup.py" -s "tests/simpletypes_other2_sub.py" --super="simpletypes_other2_sup" tests/simpletypes_other.xsd
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


class simpleTypeTestsType(GeneratedsSuper):
    __hash__ = GeneratedsSuper.__hash__
    member_data_items_ = [
        MemberSpec_('simpleTypeTest', 'simpleTypeTestDefs', 1, 0, {'maxOccurs': 'unbounded', 'name': 'simpleTypeTest', 'type': 'simpleTypeTestDefs'}, None),
        MemberSpec_('simpleContentTest', 'simpleContentType', 0, 0, {'default': 'null_string', 'name': 'simpleContentTest', 'type': 'simpleContentType'}, None),
    ]
    subclass = None
    superclass = None
    def __init__(self, simpleTypeTest=None, simpleContentTest=None, gds_collector_=None, **kwargs_):
        self.gds_collector_ = gds_collector_
        self.gds_elementtree_node_ = None
        self.original_tagname_ = None
        self.parent_object_ = kwargs_.get('parent_object_')
        self.ns_prefix_ = None
        if simpleTypeTest is None:
            self.simpleTypeTest = []
        else:
            self.simpleTypeTest = simpleTypeTest
        self.simpleTypeTest_nsprefix_ = None
        if simpleContentTest is None:
            self.simpleContentTest = globals()['simpleContentType']('null_string')
        else:
            self.simpleContentTest = simpleContentTest
        self.simpleContentTest_nsprefix_ = None
    def factory(*args_, **kwargs_):
        if CurrentSubclassModule_ is not None:
            subclass = getSubclassFromModule_(
                CurrentSubclassModule_, simpleTypeTestsType)
            if subclass is not None:
                return subclass(*args_, **kwargs_)
        if simpleTypeTestsType.subclass:
            return simpleTypeTestsType.subclass(*args_, **kwargs_)
        else:
            return simpleTypeTestsType(*args_, **kwargs_)
    factory = staticmethod(factory)
    def get_ns_prefix_(self):
        return self.ns_prefix_
    def set_ns_prefix_(self, ns_prefix):
        self.ns_prefix_ = ns_prefix
    def get_simpleTypeTest(self):
        return self.simpleTypeTest
    def set_simpleTypeTest(self, simpleTypeTest):
        self.simpleTypeTest = simpleTypeTest
    def add_simpleTypeTest(self, value):
        self.simpleTypeTest.append(value)
    def insert_simpleTypeTest_at(self, index, value):
        self.simpleTypeTest.insert(index, value)
    def replace_simpleTypeTest_at(self, index, value):
        self.simpleTypeTest[index] = value
    def get_simpleContentTest(self):
        return self.simpleContentTest
    def set_simpleContentTest(self, simpleContentTest):
        self.simpleContentTest = simpleContentTest
    def _hasContent(self):
        if (
            self.simpleTypeTest or
            self.simpleContentTest is not None
        ):
            return True
        else:
            return False
    def export(self, outfile, level, namespaceprefix_='', namespacedef_='', name_='simpleTypeTestsType', pretty_print=True):
        imported_ns_def_ = GenerateDSNamespaceDefs_.get('simpleTypeTestsType')
        if imported_ns_def_ is not None:
            namespacedef_ = imported_ns_def_
        if pretty_print:
            eol_ = '\n'
        else:
            eol_ = ''
        if self.original_tagname_ is not None and name_ == 'simpleTypeTestsType':
            name_ = self.original_tagname_
        if UseCapturedNS_ and self.ns_prefix_:
            namespaceprefix_ = self.ns_prefix_ + ':'
        showIndent(outfile, level, pretty_print)
        outfile.write('<%s%s%s' % (namespaceprefix_, name_, namespacedef_ and ' ' + namespacedef_ or '', ))
        already_processed = set()
        self._exportAttributes(outfile, level, already_processed, namespaceprefix_, name_='simpleTypeTestsType')
        if self._hasContent():
            outfile.write('>%s' % (eol_, ))
            self._exportChildren(outfile, level + 1, namespaceprefix_, namespacedef_, name_='simpleTypeTestsType', pretty_print=pretty_print)
            showIndent(outfile, level, pretty_print)
            outfile.write('</%s%s>%s' % (namespaceprefix_, name_, eol_))
        else:
            outfile.write('/>%s' % (eol_, ))
    def _exportAttributes(self, outfile, level, already_processed, namespaceprefix_='', name_='simpleTypeTestsType'):
        pass
    def _exportChildren(self, outfile, level, namespaceprefix_='', namespacedef_='', name_='simpleTypeTestsType', fromsubclass_=False, pretty_print=True):
        if pretty_print:
            eol_ = '\n'
        else:
            eol_ = ''
        for simpleTypeTest_ in self.simpleTypeTest:
            namespaceprefix_ = self.simpleTypeTest_nsprefix_ + ':' if (UseCapturedNS_ and self.simpleTypeTest_nsprefix_) else ''
            simpleTypeTest_.export(outfile, level, namespaceprefix_, namespacedef_='', name_='simpleTypeTest', pretty_print=pretty_print)
        if self.simpleContentTest is not None:
            namespaceprefix_ = self.simpleContentTest_nsprefix_ + ':' if (UseCapturedNS_ and self.simpleContentTest_nsprefix_) else ''
            self.simpleContentTest.export(outfile, level, namespaceprefix_, namespacedef_='', name_='simpleContentTest', pretty_print=pretty_print)
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
        if nodeName_ == 'simpleTypeTest':
            obj_ = simpleTypeTestDefs.factory(parent_object_=self)
            obj_.build(child_, gds_collector_=gds_collector_)
            self.simpleTypeTest.append(obj_)
            obj_.original_tagname_ = 'simpleTypeTest'
        elif nodeName_ == 'simpleContentTest':
            obj_ = simpleContentType.factory(parent_object_=self)
            obj_.build(child_, gds_collector_=gds_collector_)
            self.simpleContentTest = obj_
            obj_.original_tagname_ = 'simpleContentTest'
# end class simpleTypeTestsType


class simpleContentType(GeneratedsSuper):
    __hash__ = GeneratedsSuper.__hash__
    member_data_items_ = [
        MemberSpec_('lang', 'xs:normalizedString', 0, 1, {'use': 'optional', 'name': 'lang'}),
        MemberSpec_('identifier', 'xs:normalizedString', 0, 1, {'use': 'optional', 'name': 'identifier'}),
        MemberSpec_('valueOf_', 'xs:normalizedString', 0),
    ]
    subclass = None
    superclass = None
    def __init__(self, lang=None, identifier=None, valueOf_=None, gds_collector_=None, **kwargs_):
        self.gds_collector_ = gds_collector_
        self.gds_elementtree_node_ = None
        self.original_tagname_ = None
        self.parent_object_ = kwargs_.get('parent_object_')
        self.ns_prefix_ = None
        self.lang = _cast(None, lang)
        self.lang_nsprefix_ = None
        self.identifier = _cast(None, identifier)
        self.identifier_nsprefix_ = None
        self.valueOf_ = valueOf_
    def factory(*args_, **kwargs_):
        if CurrentSubclassModule_ is not None:
            subclass = getSubclassFromModule_(
                CurrentSubclassModule_, simpleContentType)
            if subclass is not None:
                return subclass(*args_, **kwargs_)
        if simpleContentType.subclass:
            return simpleContentType.subclass(*args_, **kwargs_)
        else:
            return simpleContentType(*args_, **kwargs_)
    factory = staticmethod(factory)
    def get_ns_prefix_(self):
        return self.ns_prefix_
    def set_ns_prefix_(self, ns_prefix):
        self.ns_prefix_ = ns_prefix
    def get_lang(self):
        return self.lang
    def set_lang(self, lang):
        self.lang = lang
    def get_identifier(self):
        return self.identifier
    def set_identifier(self, identifier):
        self.identifier = identifier
    def get_valueOf_(self): return self.valueOf_
    def set_valueOf_(self, valueOf_): self.valueOf_ = valueOf_
    def _hasContent(self):
        if (
            (1 if type(self.valueOf_) in [int,float] else self.valueOf_)
        ):
            return True
        else:
            return False
    def export(self, outfile, level, namespaceprefix_='', namespacedef_='', name_='simpleContentType', pretty_print=True):
        imported_ns_def_ = GenerateDSNamespaceDefs_.get('simpleContentType')
        if imported_ns_def_ is not None:
            namespacedef_ = imported_ns_def_
        if pretty_print:
            eol_ = '\n'
        else:
            eol_ = ''
        if self.original_tagname_ is not None and name_ == 'simpleContentType':
            name_ = self.original_tagname_
        if UseCapturedNS_ and self.ns_prefix_:
            namespaceprefix_ = self.ns_prefix_ + ':'
        showIndent(outfile, level, pretty_print)
        outfile.write('<%s%s%s' % (namespaceprefix_, name_, namespacedef_ and ' ' + namespacedef_ or '', ))
        already_processed = set()
        self._exportAttributes(outfile, level, already_processed, namespaceprefix_, name_='simpleContentType')
        if self._hasContent():
            outfile.write('>')
            outfile.write(self.convert_unicode(self.valueOf_))
            self._exportChildren(outfile, level + 1, namespaceprefix_, namespacedef_, name_='simpleContentType', pretty_print=pretty_print)
            outfile.write('</%s%s>%s' % (namespaceprefix_, name_, eol_))
        else:
            outfile.write('/>%s' % (eol_, ))
    def _exportAttributes(self, outfile, level, already_processed, namespaceprefix_='', name_='simpleContentType'):
        if self.lang is not None and 'lang' not in already_processed:
            already_processed.add('lang')
            outfile.write(' lang=%s' % (self.gds_encode(self.gds_format_string(quote_attrib(self.lang), input_name='lang')), ))
        if self.identifier is not None and 'identifier' not in already_processed:
            already_processed.add('identifier')
            outfile.write(' identifier=%s' % (self.gds_encode(self.gds_format_string(quote_attrib(self.identifier), input_name='identifier')), ))
    def _exportChildren(self, outfile, level, namespaceprefix_='', namespacedef_='', name_='simpleContentType', fromsubclass_=False, pretty_print=True):
        pass
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
        value = find_attr_value_('lang', node)
        if value is not None and 'lang' not in already_processed:
            already_processed.add('lang')
            self.lang = value
        value = find_attr_value_('identifier', node)
        if value is not None and 'identifier' not in already_processed:
            already_processed.add('identifier')
            self.identifier = value
    def _buildChildren(self, child_, node, nodeName_, fromsubclass_=False, gds_collector_=None):
        pass
# end class simpleContentType


class simpleTypeTestDefs(GeneratedsSuper):
    __hash__ = GeneratedsSuper.__hash__
    member_data_items_ = [
        MemberSpec_('datetime1', 'xs:gYear', 0, 0, {'name': 'datetime1', 'type': 'xs:gYear'}, None),
        MemberSpec_('datetime2', 'xs:gYearMonth', 0, 0, {'name': 'datetime2', 'type': 'xs:gYearMonth'}, None),
        MemberSpec_('datetime3', 'xs:gMonth', 0, 0, {'name': 'datetime3', 'type': 'xs:gMonth'}, None),
        MemberSpec_('datetime4', 'xs:gMonthDay', 0, 0, {'name': 'datetime4', 'type': 'xs:gMonthDay'}, None),
        MemberSpec_('datetime5', 'xs:gDay', 0, 0, {'name': 'datetime5', 'type': 'xs:gDay'}, None),
        MemberSpec_('integerVal1', 'xs:integer', 0, 0, {'name': 'integerVal1', 'type': 'xs:integer'}, None),
        MemberSpec_('integerVal2', 'xs:integer', 1, 1, {'maxOccurs': 'unbounded', 'minOccurs': '0', 'name': 'integerVal2', 'type': 'xs:integer'}, None),
        MemberSpec_('stringVal1', 'xs:string', 0, 0, {'name': 'stringVal1', 'type': 'xs:string'}, None),
        MemberSpec_('stringVal2', 'xs:string', 1, 1, {'maxOccurs': 'unbounded', 'minOccurs': '0', 'name': 'stringVal2', 'type': 'xs:string'}, None),
        MemberSpec_('booleanVal1', 'xs:boolean', 0, 0, {'name': 'booleanVal1', 'type': 'xs:boolean'}, None),
        MemberSpec_('booleanVal2', 'xs:boolean', 1, 1, {'maxOccurs': 'unbounded', 'minOccurs': '0', 'name': 'booleanVal2', 'type': 'xs:boolean'}, None),
        MemberSpec_('decimalVal1', 'xs:decimal', 0, 0, {'name': 'decimalVal1', 'type': 'xs:decimal'}, None),
        MemberSpec_('decimalVal2', 'xs:decimal', 1, 1, {'maxOccurs': 'unbounded', 'minOccurs': '0', 'name': 'decimalVal2', 'type': 'xs:decimal'}, None),
        MemberSpec_('doubleVal1', 'xs:double', 0, 0, {'name': 'doubleVal1', 'type': 'xs:double'}, None),
        MemberSpec_('doubleVal2', 'xs:double', 1, 1, {'maxOccurs': 'unbounded', 'minOccurs': '0', 'name': 'doubleVal2', 'type': 'xs:double'}, None),
        MemberSpec_('floatVal1', 'xs:float', 0, 0, {'name': 'floatVal1', 'type': 'xs:float'}, None),
        MemberSpec_('floatVal2', 'xs:float', 1, 1, {'maxOccurs': 'unbounded', 'minOccurs': '0', 'name': 'floatVal2', 'type': 'xs:float'}, None),
        MemberSpec_('dateVal1', 'xs:date', 0, 0, {'name': 'dateVal1', 'type': 'xs:date'}, None),
        MemberSpec_('dateVal2', 'xs:date', 1, 1, {'maxOccurs': 'unbounded', 'minOccurs': '0', 'name': 'dateVal2', 'type': 'xs:date'}, None),
        MemberSpec_('dateTimeVal1', 'xs:dateTime', 0, 0, {'name': 'dateTimeVal1', 'type': 'xs:dateTime'}, None),
        MemberSpec_('dateTimeVal2', 'xs:dateTime', 1, 1, {'maxOccurs': 'unbounded', 'minOccurs': '0', 'name': 'dateTimeVal2', 'type': 'xs:dateTime'}, None),
    ]
    subclass = None
    superclass = None
    def __init__(self, datetime1=None, datetime2=None, datetime3=None, datetime4=None, datetime5=None, integerVal1=None, integerVal2=None, stringVal1=None, stringVal2=None, booleanVal1=None, booleanVal2=None, decimalVal1=None, decimalVal2=None, doubleVal1=None, doubleVal2=None, floatVal1=None, floatVal2=None, dateVal1=None, dateVal2=None, dateTimeVal1=None, dateTimeVal2=None, gds_collector_=None, **kwargs_):
        self.gds_collector_ = gds_collector_
        self.gds_elementtree_node_ = None
        self.original_tagname_ = None
        self.parent_object_ = kwargs_.get('parent_object_')
        self.ns_prefix_ = None
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
        self.integerVal1 = integerVal1
        self.integerVal1_nsprefix_ = None
        if integerVal2 is None:
            self.integerVal2 = []
        else:
            self.integerVal2 = integerVal2
        self.integerVal2_nsprefix_ = None
        self.stringVal1 = stringVal1
        self.stringVal1_nsprefix_ = None
        if stringVal2 is None:
            self.stringVal2 = []
        else:
            self.stringVal2 = stringVal2
        self.stringVal2_nsprefix_ = None
        self.booleanVal1 = booleanVal1
        self.booleanVal1_nsprefix_ = None
        if booleanVal2 is None:
            self.booleanVal2 = []
        else:
            self.booleanVal2 = booleanVal2
        self.booleanVal2_nsprefix_ = None
        self.decimalVal1 = decimalVal1
        self.decimalVal1_nsprefix_ = None
        if decimalVal2 is None:
            self.decimalVal2 = []
        else:
            self.decimalVal2 = decimalVal2
        self.decimalVal2_nsprefix_ = None
        self.doubleVal1 = doubleVal1
        self.doubleVal1_nsprefix_ = None
        if doubleVal2 is None:
            self.doubleVal2 = []
        else:
            self.doubleVal2 = doubleVal2
        self.doubleVal2_nsprefix_ = None
        self.floatVal1 = floatVal1
        self.floatVal1_nsprefix_ = None
        if floatVal2 is None:
            self.floatVal2 = []
        else:
            self.floatVal2 = floatVal2
        self.floatVal2_nsprefix_ = None
        if isinstance(dateVal1, BaseStrType_):
            initvalue_ = datetime_.datetime.strptime(dateVal1, '%Y-%m-%d').date()
        else:
            initvalue_ = dateVal1
        self.dateVal1 = initvalue_
        self.dateVal1_nsprefix_ = None
        if dateVal2 is None:
            self.dateVal2 = []
        else:
            self.dateVal2 = dateVal2
        self.dateVal2_nsprefix_ = None
        if isinstance(dateTimeVal1, BaseStrType_):
            initvalue_ = datetime_.datetime.strptime(dateTimeVal1, '%Y-%m-%dT%H:%M:%S')
        else:
            initvalue_ = dateTimeVal1
        self.dateTimeVal1 = initvalue_
        self.dateTimeVal1_nsprefix_ = None
        if dateTimeVal2 is None:
            self.dateTimeVal2 = []
        else:
            self.dateTimeVal2 = dateTimeVal2
        self.dateTimeVal2_nsprefix_ = None
    def factory(*args_, **kwargs_):
        if CurrentSubclassModule_ is not None:
            subclass = getSubclassFromModule_(
                CurrentSubclassModule_, simpleTypeTestDefs)
            if subclass is not None:
                return subclass(*args_, **kwargs_)
        if simpleTypeTestDefs.subclass:
            return simpleTypeTestDefs.subclass(*args_, **kwargs_)
        else:
            return simpleTypeTestDefs(*args_, **kwargs_)
    factory = staticmethod(factory)
    def get_ns_prefix_(self):
        return self.ns_prefix_
    def set_ns_prefix_(self, ns_prefix):
        self.ns_prefix_ = ns_prefix
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
    def get_integerVal1(self):
        return self.integerVal1
    def set_integerVal1(self, integerVal1):
        self.integerVal1 = integerVal1
    def get_integerVal2(self):
        return self.integerVal2
    def set_integerVal2(self, integerVal2):
        self.integerVal2 = integerVal2
    def add_integerVal2(self, value):
        self.integerVal2.append(value)
    def insert_integerVal2_at(self, index, value):
        self.integerVal2.insert(index, value)
    def replace_integerVal2_at(self, index, value):
        self.integerVal2[index] = value
    def get_stringVal1(self):
        return self.stringVal1
    def set_stringVal1(self, stringVal1):
        self.stringVal1 = stringVal1
    def get_stringVal2(self):
        return self.stringVal2
    def set_stringVal2(self, stringVal2):
        self.stringVal2 = stringVal2
    def add_stringVal2(self, value):
        self.stringVal2.append(value)
    def insert_stringVal2_at(self, index, value):
        self.stringVal2.insert(index, value)
    def replace_stringVal2_at(self, index, value):
        self.stringVal2[index] = value
    def get_booleanVal1(self):
        return self.booleanVal1
    def set_booleanVal1(self, booleanVal1):
        self.booleanVal1 = booleanVal1
    def get_booleanVal2(self):
        return self.booleanVal2
    def set_booleanVal2(self, booleanVal2):
        self.booleanVal2 = booleanVal2
    def add_booleanVal2(self, value):
        self.booleanVal2.append(value)
    def insert_booleanVal2_at(self, index, value):
        self.booleanVal2.insert(index, value)
    def replace_booleanVal2_at(self, index, value):
        self.booleanVal2[index] = value
    def get_decimalVal1(self):
        return self.decimalVal1
    def set_decimalVal1(self, decimalVal1):
        self.decimalVal1 = decimalVal1
    def get_decimalVal2(self):
        return self.decimalVal2
    def set_decimalVal2(self, decimalVal2):
        self.decimalVal2 = decimalVal2
    def add_decimalVal2(self, value):
        self.decimalVal2.append(value)
    def insert_decimalVal2_at(self, index, value):
        self.decimalVal2.insert(index, value)
    def replace_decimalVal2_at(self, index, value):
        self.decimalVal2[index] = value
    def get_doubleVal1(self):
        return self.doubleVal1
    def set_doubleVal1(self, doubleVal1):
        self.doubleVal1 = doubleVal1
    def get_doubleVal2(self):
        return self.doubleVal2
    def set_doubleVal2(self, doubleVal2):
        self.doubleVal2 = doubleVal2
    def add_doubleVal2(self, value):
        self.doubleVal2.append(value)
    def insert_doubleVal2_at(self, index, value):
        self.doubleVal2.insert(index, value)
    def replace_doubleVal2_at(self, index, value):
        self.doubleVal2[index] = value
    def get_floatVal1(self):
        return self.floatVal1
    def set_floatVal1(self, floatVal1):
        self.floatVal1 = floatVal1
    def get_floatVal2(self):
        return self.floatVal2
    def set_floatVal2(self, floatVal2):
        self.floatVal2 = floatVal2
    def add_floatVal2(self, value):
        self.floatVal2.append(value)
    def insert_floatVal2_at(self, index, value):
        self.floatVal2.insert(index, value)
    def replace_floatVal2_at(self, index, value):
        self.floatVal2[index] = value
    def get_dateVal1(self):
        return self.dateVal1
    def set_dateVal1(self, dateVal1):
        self.dateVal1 = dateVal1
    def get_dateVal2(self):
        return self.dateVal2
    def set_dateVal2(self, dateVal2):
        self.dateVal2 = dateVal2
    def add_dateVal2(self, value):
        self.dateVal2.append(value)
    def insert_dateVal2_at(self, index, value):
        self.dateVal2.insert(index, value)
    def replace_dateVal2_at(self, index, value):
        self.dateVal2[index] = value
    def get_dateTimeVal1(self):
        return self.dateTimeVal1
    def set_dateTimeVal1(self, dateTimeVal1):
        self.dateTimeVal1 = dateTimeVal1
    def get_dateTimeVal2(self):
        return self.dateTimeVal2
    def set_dateTimeVal2(self, dateTimeVal2):
        self.dateTimeVal2 = dateTimeVal2
    def add_dateTimeVal2(self, value):
        self.dateTimeVal2.append(value)
    def insert_dateTimeVal2_at(self, index, value):
        self.dateTimeVal2.insert(index, value)
    def replace_dateTimeVal2_at(self, index, value):
        self.dateTimeVal2[index] = value
    def _hasContent(self):
        if (
            self.datetime1 is not None or
            self.datetime2 is not None or
            self.datetime3 is not None or
            self.datetime4 is not None or
            self.datetime5 is not None or
            self.integerVal1 is not None or
            self.integerVal2 or
            self.stringVal1 is not None or
            self.stringVal2 or
            self.booleanVal1 is not None or
            self.booleanVal2 or
            self.decimalVal1 is not None or
            self.decimalVal2 or
            self.doubleVal1 is not None or
            self.doubleVal2 or
            self.floatVal1 is not None or
            self.floatVal2 or
            self.dateVal1 is not None or
            self.dateVal2 or
            self.dateTimeVal1 is not None or
            self.dateTimeVal2
        ):
            return True
        else:
            return False
    def export(self, outfile, level, namespaceprefix_='', namespacedef_='', name_='simpleTypeTestDefs', pretty_print=True):
        imported_ns_def_ = GenerateDSNamespaceDefs_.get('simpleTypeTestDefs')
        if imported_ns_def_ is not None:
            namespacedef_ = imported_ns_def_
        if pretty_print:
            eol_ = '\n'
        else:
            eol_ = ''
        if self.original_tagname_ is not None and name_ == 'simpleTypeTestDefs':
            name_ = self.original_tagname_
        if UseCapturedNS_ and self.ns_prefix_:
            namespaceprefix_ = self.ns_prefix_ + ':'
        showIndent(outfile, level, pretty_print)
        outfile.write('<%s%s%s' % (namespaceprefix_, name_, namespacedef_ and ' ' + namespacedef_ or '', ))
        already_processed = set()
        self._exportAttributes(outfile, level, already_processed, namespaceprefix_, name_='simpleTypeTestDefs')
        if self._hasContent():
            outfile.write('>%s' % (eol_, ))
            self._exportChildren(outfile, level + 1, namespaceprefix_, namespacedef_, name_='simpleTypeTestDefs', pretty_print=pretty_print)
            showIndent(outfile, level, pretty_print)
            outfile.write('</%s%s>%s' % (namespaceprefix_, name_, eol_))
        else:
            outfile.write('/>%s' % (eol_, ))
    def _exportAttributes(self, outfile, level, already_processed, namespaceprefix_='', name_='simpleTypeTestDefs'):
        pass
    def _exportChildren(self, outfile, level, namespaceprefix_='', namespacedef_='', name_='simpleTypeTestDefs', fromsubclass_=False, pretty_print=True):
        if pretty_print:
            eol_ = '\n'
        else:
            eol_ = ''
        if self.datetime1 is not None:
            namespaceprefix_ = self.datetime1_nsprefix_ + ':' if (UseCapturedNS_ and self.datetime1_nsprefix_) else ''
            showIndent(outfile, level, pretty_print)
            outfile.write('<%sdatetime1>%s</%sdatetime1>%s' % (namespaceprefix_ , self.gds_encode(self.gds_format_string(quote_xml(self.datetime1), input_name='datetime1')), namespaceprefix_ , eol_))
        if self.datetime2 is not None:
            namespaceprefix_ = self.datetime2_nsprefix_ + ':' if (UseCapturedNS_ and self.datetime2_nsprefix_) else ''
            showIndent(outfile, level, pretty_print)
            outfile.write('<%sdatetime2>%s</%sdatetime2>%s' % (namespaceprefix_ , self.gds_encode(self.gds_format_string(quote_xml(self.datetime2), input_name='datetime2')), namespaceprefix_ , eol_))
        if self.datetime3 is not None:
            namespaceprefix_ = self.datetime3_nsprefix_ + ':' if (UseCapturedNS_ and self.datetime3_nsprefix_) else ''
            showIndent(outfile, level, pretty_print)
            outfile.write('<%sdatetime3>%s</%sdatetime3>%s' % (namespaceprefix_ , self.gds_encode(self.gds_format_string(quote_xml(self.datetime3), input_name='datetime3')), namespaceprefix_ , eol_))
        if self.datetime4 is not None:
            namespaceprefix_ = self.datetime4_nsprefix_ + ':' if (UseCapturedNS_ and self.datetime4_nsprefix_) else ''
            showIndent(outfile, level, pretty_print)
            outfile.write('<%sdatetime4>%s</%sdatetime4>%s' % (namespaceprefix_ , self.gds_encode(self.gds_format_string(quote_xml(self.datetime4), input_name='datetime4')), namespaceprefix_ , eol_))
        if self.datetime5 is not None:
            namespaceprefix_ = self.datetime5_nsprefix_ + ':' if (UseCapturedNS_ and self.datetime5_nsprefix_) else ''
            showIndent(outfile, level, pretty_print)
            outfile.write('<%sdatetime5>%s</%sdatetime5>%s' % (namespaceprefix_ , self.gds_encode(self.gds_format_string(quote_xml(self.datetime5), input_name='datetime5')), namespaceprefix_ , eol_))
        if self.integerVal1 is not None:
            namespaceprefix_ = self.integerVal1_nsprefix_ + ':' if (UseCapturedNS_ and self.integerVal1_nsprefix_) else ''
            showIndent(outfile, level, pretty_print)
            outfile.write('<%sintegerVal1>%s</%sintegerVal1>%s' % (namespaceprefix_ , self.gds_format_integer(self.integerVal1, input_name='integerVal1'), namespaceprefix_ , eol_))
        for integerVal2_ in self.integerVal2:
            namespaceprefix_ = self.integerVal2_nsprefix_ + ':' if (UseCapturedNS_ and self.integerVal2_nsprefix_) else ''
            showIndent(outfile, level, pretty_print)
            outfile.write('<%sintegerVal2>%s</%sintegerVal2>%s' % (namespaceprefix_ , self.gds_format_integer(integerVal2_, input_name='integerVal2'), namespaceprefix_ , eol_))
        if self.stringVal1 is not None:
            namespaceprefix_ = self.stringVal1_nsprefix_ + ':' if (UseCapturedNS_ and self.stringVal1_nsprefix_) else ''
            showIndent(outfile, level, pretty_print)
            outfile.write('<%sstringVal1>%s</%sstringVal1>%s' % (namespaceprefix_ , self.gds_encode(self.gds_format_string(quote_xml(self.stringVal1), input_name='stringVal1')), namespaceprefix_ , eol_))
        for stringVal2_ in self.stringVal2:
            namespaceprefix_ = self.stringVal2_nsprefix_ + ':' if (UseCapturedNS_ and self.stringVal2_nsprefix_) else ''
            showIndent(outfile, level, pretty_print)
            outfile.write('<%sstringVal2>%s</%sstringVal2>%s' % (namespaceprefix_ , self.gds_encode(self.gds_format_string(quote_xml(stringVal2_), input_name='stringVal2')), namespaceprefix_ , eol_))
        if self.booleanVal1 is not None:
            namespaceprefix_ = self.booleanVal1_nsprefix_ + ':' if (UseCapturedNS_ and self.booleanVal1_nsprefix_) else ''
            showIndent(outfile, level, pretty_print)
            outfile.write('<%sbooleanVal1>%s</%sbooleanVal1>%s' % (namespaceprefix_ , self.gds_format_boolean(self.booleanVal1, input_name='booleanVal1'), namespaceprefix_ , eol_))
        for booleanVal2_ in self.booleanVal2:
            namespaceprefix_ = self.booleanVal2_nsprefix_ + ':' if (UseCapturedNS_ and self.booleanVal2_nsprefix_) else ''
            showIndent(outfile, level, pretty_print)
            outfile.write('<%sbooleanVal2>%s</%sbooleanVal2>%s' % (namespaceprefix_ , self.gds_format_boolean(booleanVal2_, input_name='booleanVal2'), namespaceprefix_ , eol_))
        if self.decimalVal1 is not None:
            namespaceprefix_ = self.decimalVal1_nsprefix_ + ':' if (UseCapturedNS_ and self.decimalVal1_nsprefix_) else ''
            showIndent(outfile, level, pretty_print)
            outfile.write('<%sdecimalVal1>%s</%sdecimalVal1>%s' % (namespaceprefix_ , self.gds_format_decimal(self.decimalVal1, input_name='decimalVal1'), namespaceprefix_ , eol_))
        for decimalVal2_ in self.decimalVal2:
            namespaceprefix_ = self.decimalVal2_nsprefix_ + ':' if (UseCapturedNS_ and self.decimalVal2_nsprefix_) else ''
            showIndent(outfile, level, pretty_print)
            outfile.write('<%sdecimalVal2>%s</%sdecimalVal2>%s' % (namespaceprefix_ , self.gds_format_decimal(decimalVal2_, input_name='decimalVal2'), namespaceprefix_ , eol_))
        if self.doubleVal1 is not None:
            namespaceprefix_ = self.doubleVal1_nsprefix_ + ':' if (UseCapturedNS_ and self.doubleVal1_nsprefix_) else ''
            showIndent(outfile, level, pretty_print)
            outfile.write('<%sdoubleVal1>%s</%sdoubleVal1>%s' % (namespaceprefix_ , self.gds_format_double(self.doubleVal1, input_name='doubleVal1'), namespaceprefix_ , eol_))
        for doubleVal2_ in self.doubleVal2:
            namespaceprefix_ = self.doubleVal2_nsprefix_ + ':' if (UseCapturedNS_ and self.doubleVal2_nsprefix_) else ''
            showIndent(outfile, level, pretty_print)
            outfile.write('<%sdoubleVal2>%s</%sdoubleVal2>%s' % (namespaceprefix_ , self.gds_format_double(doubleVal2_, input_name='doubleVal2'), namespaceprefix_ , eol_))
        if self.floatVal1 is not None:
            namespaceprefix_ = self.floatVal1_nsprefix_ + ':' if (UseCapturedNS_ and self.floatVal1_nsprefix_) else ''
            showIndent(outfile, level, pretty_print)
            outfile.write('<%sfloatVal1>%s</%sfloatVal1>%s' % (namespaceprefix_ , self.gds_format_float(self.floatVal1, input_name='floatVal1'), namespaceprefix_ , eol_))
        for floatVal2_ in self.floatVal2:
            namespaceprefix_ = self.floatVal2_nsprefix_ + ':' if (UseCapturedNS_ and self.floatVal2_nsprefix_) else ''
            showIndent(outfile, level, pretty_print)
            outfile.write('<%sfloatVal2>%s</%sfloatVal2>%s' % (namespaceprefix_ , self.gds_format_float(floatVal2_, input_name='floatVal2'), namespaceprefix_ , eol_))
        if self.dateVal1 is not None:
            namespaceprefix_ = self.dateVal1_nsprefix_ + ':' if (UseCapturedNS_ and self.dateVal1_nsprefix_) else ''
            showIndent(outfile, level, pretty_print)
            outfile.write('<%sdateVal1>%s</%sdateVal1>%s' % (namespaceprefix_ , self.gds_format_date(self.dateVal1, input_name='dateVal1'), namespaceprefix_ , eol_))
        for dateVal2_ in self.dateVal2:
            namespaceprefix_ = self.dateVal2_nsprefix_ + ':' if (UseCapturedNS_ and self.dateVal2_nsprefix_) else ''
            showIndent(outfile, level, pretty_print)
            outfile.write('<%sdateVal2>%s</%sdateVal2>%s' % (namespaceprefix_ , self.gds_format_date(dateVal2_, input_name='dateVal2'), namespaceprefix_ , eol_))
        if self.dateTimeVal1 is not None:
            namespaceprefix_ = self.dateTimeVal1_nsprefix_ + ':' if (UseCapturedNS_ and self.dateTimeVal1_nsprefix_) else ''
            showIndent(outfile, level, pretty_print)
            outfile.write('<%sdateTimeVal1>%s</%sdateTimeVal1>%s' % (namespaceprefix_ , self.gds_format_datetime(self.dateTimeVal1, input_name='dateTimeVal1'), namespaceprefix_ , eol_))
        for dateTimeVal2_ in self.dateTimeVal2:
            namespaceprefix_ = self.dateTimeVal2_nsprefix_ + ':' if (UseCapturedNS_ and self.dateTimeVal2_nsprefix_) else ''
            showIndent(outfile, level, pretty_print)
            outfile.write('<%sdateTimeVal2>%s</%sdateTimeVal2>%s' % (namespaceprefix_ , self.gds_format_datetime(dateTimeVal2_, input_name='dateTimeVal2'), namespaceprefix_ , eol_))
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
        if nodeName_ == 'datetime1':
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
        elif nodeName_ == 'integerVal1' and child_.text:
            sval_ = child_.text
            ival_ = self.gds_parse_integer(sval_, node, 'integerVal1')
            ival_ = self.gds_validate_integer(ival_, node, 'integerVal1')
            self.integerVal1 = ival_
            self.integerVal1_nsprefix_ = child_.prefix
        elif nodeName_ == 'integerVal2' and child_.text:
            sval_ = child_.text
            ival_ = self.gds_parse_integer(sval_, node, 'integerVal2')
            ival_ = self.gds_validate_integer(ival_, node, 'integerVal2')
            self.integerVal2.append(ival_)
            self.integerVal2_nsprefix_ = child_.prefix
        elif nodeName_ == 'stringVal1':
            value_ = child_.text
            value_ = self.gds_parse_string(value_, node, 'stringVal1')
            value_ = self.gds_validate_string(value_, node, 'stringVal1')
            self.stringVal1 = value_
            self.stringVal1_nsprefix_ = child_.prefix
        elif nodeName_ == 'stringVal2':
            value_ = child_.text
            value_ = self.gds_parse_string(value_, node, 'stringVal2')
            value_ = self.gds_validate_string(value_, node, 'stringVal2')
            self.stringVal2.append(value_)
            self.stringVal2_nsprefix_ = child_.prefix
        elif nodeName_ == 'booleanVal1':
            sval_ = child_.text
            ival_ = self.gds_parse_boolean(sval_, node, 'booleanVal1')
            ival_ = self.gds_validate_boolean(ival_, node, 'booleanVal1')
            self.booleanVal1 = ival_
            self.booleanVal1_nsprefix_ = child_.prefix
        elif nodeName_ == 'booleanVal2':
            sval_ = child_.text
            ival_ = self.gds_parse_boolean(sval_, node, 'booleanVal2')
            ival_ = self.gds_validate_boolean(ival_, node, 'booleanVal2')
            self.booleanVal2.append(ival_)
            self.booleanVal2_nsprefix_ = child_.prefix
        elif nodeName_ == 'decimalVal1' and child_.text:
            sval_ = child_.text
            fval_ = self.gds_parse_decimal(sval_, node, 'decimalVal1')
            fval_ = self.gds_validate_decimal(fval_, node, 'decimalVal1')
            self.decimalVal1 = fval_
            self.decimalVal1_nsprefix_ = child_.prefix
        elif nodeName_ == 'decimalVal2' and child_.text:
            sval_ = child_.text
            fval_ = self.gds_parse_decimal(sval_, node, 'decimalVal2')
            fval_ = self.gds_validate_decimal(fval_, node, 'decimalVal2')
            self.decimalVal2.append(fval_)
            self.decimalVal2_nsprefix_ = child_.prefix
        elif nodeName_ == 'doubleVal1' and child_.text:
            sval_ = child_.text
            fval_ = self.gds_parse_double(sval_, node, 'doubleVal1')
            fval_ = self.gds_validate_double(fval_, node, 'doubleVal1')
            self.doubleVal1 = fval_
            self.doubleVal1_nsprefix_ = child_.prefix
        elif nodeName_ == 'doubleVal2' and child_.text:
            sval_ = child_.text
            fval_ = self.gds_parse_double(sval_, node, 'doubleVal2')
            fval_ = self.gds_validate_double(fval_, node, 'doubleVal2')
            self.doubleVal2.append(fval_)
            self.doubleVal2_nsprefix_ = child_.prefix
        elif nodeName_ == 'floatVal1' and child_.text:
            sval_ = child_.text
            fval_ = self.gds_parse_float(sval_, node, 'floatVal1')
            fval_ = self.gds_validate_float(fval_, node, 'floatVal1')
            self.floatVal1 = fval_
            self.floatVal1_nsprefix_ = child_.prefix
        elif nodeName_ == 'floatVal2' and child_.text:
            sval_ = child_.text
            fval_ = self.gds_parse_float(sval_, node, 'floatVal2')
            fval_ = self.gds_validate_float(fval_, node, 'floatVal2')
            self.floatVal2.append(fval_)
            self.floatVal2_nsprefix_ = child_.prefix
        elif nodeName_ == 'dateVal1':
            sval_ = child_.text
            dval_ = self.gds_parse_date(sval_)
            self.dateVal1 = dval_
            self.dateVal1_nsprefix_ = child_.prefix
        elif nodeName_ == 'dateVal2':
            sval_ = child_.text
            dval_ = self.gds_parse_date(sval_)
            self.dateVal2.append(dval_)
            self.dateVal2_nsprefix_ = child_.prefix
        elif nodeName_ == 'dateTimeVal1':
            sval_ = child_.text
            dval_ = self.gds_parse_datetime(sval_)
            self.dateTimeVal1 = dval_
            self.dateTimeVal1_nsprefix_ = child_.prefix
        elif nodeName_ == 'dateTimeVal2':
            sval_ = child_.text
            dval_ = self.gds_parse_datetime(sval_)
            self.dateTimeVal2.append(dval_)
            self.dateTimeVal2_nsprefix_ = child_.prefix
# end class simpleTypeTestDefs


GDSClassesMapping = {
    'simpleTypeTests': simpleTypeTestsType,
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
        rootTag = 'simpleTypeTestsType'
        rootClass = simpleTypeTestsType
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
        rootTag = 'simpleTypeTestsType'
        rootClass = simpleTypeTestsType
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
        rootTag = 'simpleTypeTestsType'
        rootClass = simpleTypeTestsType
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
        rootTag = 'simpleTypeTestsType'
        rootClass = simpleTypeTestsType
    rootObj = rootClass.factory()
    rootObj.build(rootNode, gds_collector_=gds_collector)
    # Enable Python to collect the space used by the DOM.
    if not SaveElementTreeNode:
        doc = None
        rootNode = None
##     if not silence:
##         sys.stdout.write('#from simpletypes_other2_sup import *\n\n')
##         sys.stdout.write('import simpletypes_other2_sup as model_\n\n')
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
    "simpleContentType",
    "simpleTypeTestDefs",
    "simpleTypeTestsType"
]
