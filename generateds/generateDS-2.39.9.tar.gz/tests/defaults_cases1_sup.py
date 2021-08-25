#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# Generated  by generateDS.py.
# Python 3.8.11 (default, Aug  3 2021, 15:09:35)  [GCC 7.5.0]
#
# Command line options:
#   ('--no-dates', '')
#   ('--no-versions', '')
#   ('--member-specs', 'list')
#   ('-f', '')
#   ('-o', 'tests/defaults_cases2_sup.py')
#   ('-s', 'tests/defaults_cases2_sub.py')
#   ('--super', 'defaults_cases2_sup')
#
# Command line arguments:
#   tests/defaults_cases.xsd
#
# Command line:
#   generateDS.py --no-dates --no-versions --member-specs="list" -f -o "tests/defaults_cases2_sup.py" -s "tests/defaults_cases2_sub.py" --super="defaults_cases2_sup" tests/defaults_cases.xsd
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


class DefaultTypes(GeneratedsSuper):
    __hash__ = GeneratedsSuper.__hash__
    member_data_items_ = [
        MemberSpec_('default1', 'DefaultType1', 1, 0, {'maxOccurs': 'unbounded', 'name': 'default1', 'type': 'DefaultType1'}, None),
        MemberSpec_('default2', 'DefaultType2', 1, 0, {'maxOccurs': 'unbounded', 'name': 'default2', 'type': 'DefaultType2'}, None),
        MemberSpec_('fixed1', 'FixedType1', 1, 0, {'maxOccurs': 'unbounded', 'name': 'fixed1', 'type': 'FixedType1'}, None),
        MemberSpec_('fixed2', 'FixedType2', 1, 0, {'maxOccurs': 'unbounded', 'name': 'fixed2', 'type': 'FixedType2'}, None),
    ]
    subclass = None
    superclass = None
    def __init__(self, default1=None, default2=None, fixed1=None, fixed2=None, gds_collector_=None, **kwargs_):
        self.gds_collector_ = gds_collector_
        self.gds_elementtree_node_ = None
        self.original_tagname_ = None
        self.parent_object_ = kwargs_.get('parent_object_')
        self.ns_prefix_ = None
        if default1 is None:
            self.default1 = []
        else:
            self.default1 = default1
        self.default1_nsprefix_ = None
        if default2 is None:
            self.default2 = []
        else:
            self.default2 = default2
        self.default2_nsprefix_ = None
        if fixed1 is None:
            self.fixed1 = []
        else:
            self.fixed1 = fixed1
        self.fixed1_nsprefix_ = None
        if fixed2 is None:
            self.fixed2 = []
        else:
            self.fixed2 = fixed2
        self.fixed2_nsprefix_ = None
    def factory(*args_, **kwargs_):
        if CurrentSubclassModule_ is not None:
            subclass = getSubclassFromModule_(
                CurrentSubclassModule_, DefaultTypes)
            if subclass is not None:
                return subclass(*args_, **kwargs_)
        if DefaultTypes.subclass:
            return DefaultTypes.subclass(*args_, **kwargs_)
        else:
            return DefaultTypes(*args_, **kwargs_)
    factory = staticmethod(factory)
    def get_ns_prefix_(self):
        return self.ns_prefix_
    def set_ns_prefix_(self, ns_prefix):
        self.ns_prefix_ = ns_prefix
    def get_default1(self):
        return self.default1
    def set_default1(self, default1):
        self.default1 = default1
    def add_default1(self, value):
        self.default1.append(value)
    def insert_default1_at(self, index, value):
        self.default1.insert(index, value)
    def replace_default1_at(self, index, value):
        self.default1[index] = value
    def get_default2(self):
        return self.default2
    def set_default2(self, default2):
        self.default2 = default2
    def add_default2(self, value):
        self.default2.append(value)
    def insert_default2_at(self, index, value):
        self.default2.insert(index, value)
    def replace_default2_at(self, index, value):
        self.default2[index] = value
    def get_fixed1(self):
        return self.fixed1
    def set_fixed1(self, fixed1):
        self.fixed1 = fixed1
    def add_fixed1(self, value):
        self.fixed1.append(value)
    def insert_fixed1_at(self, index, value):
        self.fixed1.insert(index, value)
    def replace_fixed1_at(self, index, value):
        self.fixed1[index] = value
    def get_fixed2(self):
        return self.fixed2
    def set_fixed2(self, fixed2):
        self.fixed2 = fixed2
    def add_fixed2(self, value):
        self.fixed2.append(value)
    def insert_fixed2_at(self, index, value):
        self.fixed2.insert(index, value)
    def replace_fixed2_at(self, index, value):
        self.fixed2[index] = value
    def _hasContent(self):
        if (
            self.default1 or
            self.default2 or
            self.fixed1 or
            self.fixed2
        ):
            return True
        else:
            return False
    def export(self, outfile, level, namespaceprefix_='', namespacedef_='', name_='DefaultTypes', pretty_print=True):
        imported_ns_def_ = GenerateDSNamespaceDefs_.get('DefaultTypes')
        if imported_ns_def_ is not None:
            namespacedef_ = imported_ns_def_
        if pretty_print:
            eol_ = '\n'
        else:
            eol_ = ''
        if self.original_tagname_ is not None and name_ == 'DefaultTypes':
            name_ = self.original_tagname_
        if UseCapturedNS_ and self.ns_prefix_:
            namespaceprefix_ = self.ns_prefix_ + ':'
        showIndent(outfile, level, pretty_print)
        outfile.write('<%s%s%s' % (namespaceprefix_, name_, namespacedef_ and ' ' + namespacedef_ or '', ))
        already_processed = set()
        self._exportAttributes(outfile, level, already_processed, namespaceprefix_, name_='DefaultTypes')
        if self._hasContent():
            outfile.write('>%s' % (eol_, ))
            self._exportChildren(outfile, level + 1, namespaceprefix_, namespacedef_, name_='DefaultTypes', pretty_print=pretty_print)
            showIndent(outfile, level, pretty_print)
            outfile.write('</%s%s>%s' % (namespaceprefix_, name_, eol_))
        else:
            outfile.write('/>%s' % (eol_, ))
    def _exportAttributes(self, outfile, level, already_processed, namespaceprefix_='', name_='DefaultTypes'):
        pass
    def _exportChildren(self, outfile, level, namespaceprefix_='', namespacedef_='', name_='DefaultTypes', fromsubclass_=False, pretty_print=True):
        if pretty_print:
            eol_ = '\n'
        else:
            eol_ = ''
        for default1_ in self.default1:
            namespaceprefix_ = self.default1_nsprefix_ + ':' if (UseCapturedNS_ and self.default1_nsprefix_) else ''
            default1_.export(outfile, level, namespaceprefix_, namespacedef_='', name_='default1', pretty_print=pretty_print)
        for default2_ in self.default2:
            namespaceprefix_ = self.default2_nsprefix_ + ':' if (UseCapturedNS_ and self.default2_nsprefix_) else ''
            default2_.export(outfile, level, namespaceprefix_, namespacedef_='', name_='default2', pretty_print=pretty_print)
        for fixed1_ in self.fixed1:
            namespaceprefix_ = self.fixed1_nsprefix_ + ':' if (UseCapturedNS_ and self.fixed1_nsprefix_) else ''
            fixed1_.export(outfile, level, namespaceprefix_, namespacedef_='', name_='fixed1', pretty_print=pretty_print)
        for fixed2_ in self.fixed2:
            namespaceprefix_ = self.fixed2_nsprefix_ + ':' if (UseCapturedNS_ and self.fixed2_nsprefix_) else ''
            fixed2_.export(outfile, level, namespaceprefix_, namespacedef_='', name_='fixed2', pretty_print=pretty_print)
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
        if nodeName_ == 'default1':
            obj_ = DefaultType1.factory(parent_object_=self)
            obj_.build(child_, gds_collector_=gds_collector_)
            self.default1.append(obj_)
            obj_.original_tagname_ = 'default1'
        elif nodeName_ == 'default2':
            obj_ = DefaultType2.factory(parent_object_=self)
            obj_.build(child_, gds_collector_=gds_collector_)
            self.default2.append(obj_)
            obj_.original_tagname_ = 'default2'
        elif nodeName_ == 'fixed1':
            obj_ = FixedType1.factory(parent_object_=self)
            obj_.build(child_, gds_collector_=gds_collector_)
            self.fixed1.append(obj_)
            obj_.original_tagname_ = 'fixed1'
        elif nodeName_ == 'fixed2':
            obj_ = FixedType2.factory(parent_object_=self)
            obj_.build(child_, gds_collector_=gds_collector_)
            self.fixed2.append(obj_)
            obj_.original_tagname_ = 'fixed2'
# end class DefaultTypes


class DefaultType1(GeneratedsSuper):
    __hash__ = GeneratedsSuper.__hash__
    member_data_items_ = [
        MemberSpec_('normal01', 'xs:integer', 0, 1, {'minOccurs': '0', 'name': 'normal01', 'type': 'xs:integer'}, None),
        MemberSpec_('normal02', 'xs:string', 0, 1, {'minOccurs': '0', 'name': 'normal02', 'type': 'xs:string'}, None),
        MemberSpec_('default01', 'xs:integer', 0, 1, {'default': '23', 'minOccurs': '0', 'name': 'default01', 'type': 'xs:integer'}, None),
        MemberSpec_('default02', 'xs:string', 0, 1, {'default': 'Peach', 'minOccurs': '0', 'name': 'default02', 'type': 'xs:string'}, None),
        MemberSpec_('normal03', 'xs:float', 0, 0, {'minOccurs': '1', 'name': 'normal03', 'type': 'xs:float'}, None),
        MemberSpec_('normal04', 'xs:double', 0, 0, {'minOccurs': '1', 'name': 'normal04', 'type': 'xs:double'}, None),
        MemberSpec_('default03', 'xs:float', 0, 0, {'default': '23.45', 'minOccurs': '1', 'name': 'default03', 'type': 'xs:float'}, None),
        MemberSpec_('default04', 'xs:double', 0, 0, {'default': '54.32', 'minOccurs': '1', 'name': 'default04', 'type': 'xs:double'}, None),
    ]
    subclass = None
    superclass = None
    def __init__(self, normal01=None, normal02=None, default01=23, default02='Peach', normal03=None, normal04=None, default03=23.45, default04=54.32, gds_collector_=None, **kwargs_):
        self.gds_collector_ = gds_collector_
        self.gds_elementtree_node_ = None
        self.original_tagname_ = None
        self.parent_object_ = kwargs_.get('parent_object_')
        self.ns_prefix_ = None
        self.normal01 = normal01
        self.normal01_nsprefix_ = None
        self.normal02 = normal02
        self.normal02_nsprefix_ = None
        self.default01 = default01
        self.default01_nsprefix_ = None
        self.default02 = default02
        self.default02_nsprefix_ = None
        self.normal03 = normal03
        self.normal03_nsprefix_ = None
        self.normal04 = normal04
        self.normal04_nsprefix_ = None
        self.default03 = default03
        self.default03_nsprefix_ = None
        self.default04 = default04
        self.default04_nsprefix_ = None
    def factory(*args_, **kwargs_):
        if CurrentSubclassModule_ is not None:
            subclass = getSubclassFromModule_(
                CurrentSubclassModule_, DefaultType1)
            if subclass is not None:
                return subclass(*args_, **kwargs_)
        if DefaultType1.subclass:
            return DefaultType1.subclass(*args_, **kwargs_)
        else:
            return DefaultType1(*args_, **kwargs_)
    factory = staticmethod(factory)
    def get_ns_prefix_(self):
        return self.ns_prefix_
    def set_ns_prefix_(self, ns_prefix):
        self.ns_prefix_ = ns_prefix
    def get_normal01(self):
        return self.normal01
    def set_normal01(self, normal01):
        self.normal01 = normal01
    def get_normal02(self):
        return self.normal02
    def set_normal02(self, normal02):
        self.normal02 = normal02
    def get_default01(self):
        return self.default01
    def set_default01(self, default01):
        self.default01 = default01
    def get_default02(self):
        return self.default02
    def set_default02(self, default02):
        self.default02 = default02
    def get_normal03(self):
        return self.normal03
    def set_normal03(self, normal03):
        self.normal03 = normal03
    def get_normal04(self):
        return self.normal04
    def set_normal04(self, normal04):
        self.normal04 = normal04
    def get_default03(self):
        return self.default03
    def set_default03(self, default03):
        self.default03 = default03
    def get_default04(self):
        return self.default04
    def set_default04(self, default04):
        self.default04 = default04
    def _hasContent(self):
        if (
            self.normal01 is not None or
            self.normal02 is not None or
            self.default01 != 23 or
            self.default02 != "Peach" or
            self.normal03 is not None or
            self.normal04 is not None or
            self.default03 != 23.45 or
            self.default04 != 54.32
        ):
            return True
        else:
            return False
    def export(self, outfile, level, namespaceprefix_='', namespacedef_='', name_='DefaultType1', pretty_print=True):
        imported_ns_def_ = GenerateDSNamespaceDefs_.get('DefaultType1')
        if imported_ns_def_ is not None:
            namespacedef_ = imported_ns_def_
        if pretty_print:
            eol_ = '\n'
        else:
            eol_ = ''
        if self.original_tagname_ is not None and name_ == 'DefaultType1':
            name_ = self.original_tagname_
        if UseCapturedNS_ and self.ns_prefix_:
            namespaceprefix_ = self.ns_prefix_ + ':'
        showIndent(outfile, level, pretty_print)
        outfile.write('<%s%s%s' % (namespaceprefix_, name_, namespacedef_ and ' ' + namespacedef_ or '', ))
        already_processed = set()
        self._exportAttributes(outfile, level, already_processed, namespaceprefix_, name_='DefaultType1')
        if self._hasContent():
            outfile.write('>%s' % (eol_, ))
            self._exportChildren(outfile, level + 1, namespaceprefix_, namespacedef_, name_='DefaultType1', pretty_print=pretty_print)
            showIndent(outfile, level, pretty_print)
            outfile.write('</%s%s>%s' % (namespaceprefix_, name_, eol_))
        else:
            outfile.write('/>%s' % (eol_, ))
    def _exportAttributes(self, outfile, level, already_processed, namespaceprefix_='', name_='DefaultType1'):
        pass
    def _exportChildren(self, outfile, level, namespaceprefix_='', namespacedef_='', name_='DefaultType1', fromsubclass_=False, pretty_print=True):
        if pretty_print:
            eol_ = '\n'
        else:
            eol_ = ''
        if self.normal01 is not None:
            namespaceprefix_ = self.normal01_nsprefix_ + ':' if (UseCapturedNS_ and self.normal01_nsprefix_) else ''
            showIndent(outfile, level, pretty_print)
            outfile.write('<%snormal01>%s</%snormal01>%s' % (namespaceprefix_ , self.gds_format_integer(self.normal01, input_name='normal01'), namespaceprefix_ , eol_))
        if self.normal02 is not None:
            namespaceprefix_ = self.normal02_nsprefix_ + ':' if (UseCapturedNS_ and self.normal02_nsprefix_) else ''
            showIndent(outfile, level, pretty_print)
            outfile.write('<%snormal02>%s</%snormal02>%s' % (namespaceprefix_ , self.gds_encode(self.gds_format_string(quote_xml(self.normal02), input_name='normal02')), namespaceprefix_ , eol_))
        if self.default01 != 23:
            namespaceprefix_ = self.default01_nsprefix_ + ':' if (UseCapturedNS_ and self.default01_nsprefix_) else ''
            showIndent(outfile, level, pretty_print)
            outfile.write('<%sdefault01>%s</%sdefault01>%s' % (namespaceprefix_ , self.gds_format_integer(self.default01, input_name='default01'), namespaceprefix_ , eol_))
        if self.default02 != "Peach":
            namespaceprefix_ = self.default02_nsprefix_ + ':' if (UseCapturedNS_ and self.default02_nsprefix_) else ''
            showIndent(outfile, level, pretty_print)
            outfile.write('<%sdefault02>%s</%sdefault02>%s' % (namespaceprefix_ , self.gds_encode(self.gds_format_string(quote_xml(self.default02), input_name='default02')), namespaceprefix_ , eol_))
        if self.normal03 is not None:
            namespaceprefix_ = self.normal03_nsprefix_ + ':' if (UseCapturedNS_ and self.normal03_nsprefix_) else ''
            showIndent(outfile, level, pretty_print)
            outfile.write('<%snormal03>%s</%snormal03>%s' % (namespaceprefix_ , self.gds_format_float(self.normal03, input_name='normal03'), namespaceprefix_ , eol_))
        if self.normal04 is not None:
            namespaceprefix_ = self.normal04_nsprefix_ + ':' if (UseCapturedNS_ and self.normal04_nsprefix_) else ''
            showIndent(outfile, level, pretty_print)
            outfile.write('<%snormal04>%s</%snormal04>%s' % (namespaceprefix_ , self.gds_format_double(self.normal04, input_name='normal04'), namespaceprefix_ , eol_))
        if self.default03 is not None:
            namespaceprefix_ = self.default03_nsprefix_ + ':' if (UseCapturedNS_ and self.default03_nsprefix_) else ''
            showIndent(outfile, level, pretty_print)
            outfile.write('<%sdefault03>%s</%sdefault03>%s' % (namespaceprefix_ , self.gds_format_float(self.default03, input_name='default03'), namespaceprefix_ , eol_))
        if self.default04 is not None:
            namespaceprefix_ = self.default04_nsprefix_ + ':' if (UseCapturedNS_ and self.default04_nsprefix_) else ''
            showIndent(outfile, level, pretty_print)
            outfile.write('<%sdefault04>%s</%sdefault04>%s' % (namespaceprefix_ , self.gds_format_double(self.default04, input_name='default04'), namespaceprefix_ , eol_))
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
        if nodeName_ == 'normal01' and child_.text:
            sval_ = child_.text
            ival_ = self.gds_parse_integer(sval_, node, 'normal01')
            ival_ = self.gds_validate_integer(ival_, node, 'normal01')
            self.normal01 = ival_
            self.normal01_nsprefix_ = child_.prefix
        elif nodeName_ == 'normal02':
            value_ = child_.text
            value_ = self.gds_parse_string(value_, node, 'normal02')
            value_ = self.gds_validate_string(value_, node, 'normal02')
            self.normal02 = value_
            self.normal02_nsprefix_ = child_.prefix
        elif nodeName_ == 'default01' and child_.text:
            sval_ = child_.text
            ival_ = self.gds_parse_integer(sval_, node, 'default01')
            ival_ = self.gds_validate_integer(ival_, node, 'default01')
            self.default01 = ival_
            self.default01_nsprefix_ = child_.prefix
        elif nodeName_ == 'default02':
            value_ = child_.text
            value_ = self.gds_parse_string(value_, node, 'default02')
            value_ = self.gds_validate_string(value_, node, 'default02')
            self.default02 = value_
            self.default02_nsprefix_ = child_.prefix
        elif nodeName_ == 'normal03' and child_.text:
            sval_ = child_.text
            fval_ = self.gds_parse_float(sval_, node, 'normal03')
            fval_ = self.gds_validate_float(fval_, node, 'normal03')
            self.normal03 = fval_
            self.normal03_nsprefix_ = child_.prefix
        elif nodeName_ == 'normal04' and child_.text:
            sval_ = child_.text
            fval_ = self.gds_parse_double(sval_, node, 'normal04')
            fval_ = self.gds_validate_double(fval_, node, 'normal04')
            self.normal04 = fval_
            self.normal04_nsprefix_ = child_.prefix
        elif nodeName_ == 'default03' and child_.text:
            sval_ = child_.text
            fval_ = self.gds_parse_float(sval_, node, 'default03')
            fval_ = self.gds_validate_float(fval_, node, 'default03')
            self.default03 = fval_
            self.default03_nsprefix_ = child_.prefix
        elif nodeName_ == 'default04' and child_.text:
            sval_ = child_.text
            fval_ = self.gds_parse_double(sval_, node, 'default04')
            fval_ = self.gds_validate_double(fval_, node, 'default04')
            self.default04 = fval_
            self.default04_nsprefix_ = child_.prefix
# end class DefaultType1


class DefaultType2(GeneratedsSuper):
    __hash__ = GeneratedsSuper.__hash__
    member_data_items_ = [
        MemberSpec_('attrdefault01', 'xs:string', 0, 1, {'use': 'optional', 'name': 'attrdefault01'}),
        MemberSpec_('attrdefault02', 'xs:integer', 0, 1, {'use': 'optional', 'name': 'attrdefault02'}),
        MemberSpec_('attrnormal01', 'xs:string', 0, 1, {'use': 'optional', 'name': 'attrnormal01'}),
        MemberSpec_('attrnormal02', 'xs:integer', 0, 1, {'use': 'optional', 'name': 'attrnormal02'}),
    ]
    subclass = None
    superclass = None
    def __init__(self, attrdefault01='abcd', attrdefault02=14, attrnormal01=None, attrnormal02=None, gds_collector_=None, **kwargs_):
        self.gds_collector_ = gds_collector_
        self.gds_elementtree_node_ = None
        self.original_tagname_ = None
        self.parent_object_ = kwargs_.get('parent_object_')
        self.ns_prefix_ = None
        self.attrdefault01 = _cast(None, attrdefault01)
        self.attrdefault01_nsprefix_ = None
        self.attrdefault02 = _cast(int, attrdefault02)
        self.attrdefault02_nsprefix_ = None
        self.attrnormal01 = _cast(None, attrnormal01)
        self.attrnormal01_nsprefix_ = None
        self.attrnormal02 = _cast(int, attrnormal02)
        self.attrnormal02_nsprefix_ = None
    def factory(*args_, **kwargs_):
        if CurrentSubclassModule_ is not None:
            subclass = getSubclassFromModule_(
                CurrentSubclassModule_, DefaultType2)
            if subclass is not None:
                return subclass(*args_, **kwargs_)
        if DefaultType2.subclass:
            return DefaultType2.subclass(*args_, **kwargs_)
        else:
            return DefaultType2(*args_, **kwargs_)
    factory = staticmethod(factory)
    def get_ns_prefix_(self):
        return self.ns_prefix_
    def set_ns_prefix_(self, ns_prefix):
        self.ns_prefix_ = ns_prefix
    def get_attrdefault01(self):
        return self.attrdefault01
    def set_attrdefault01(self, attrdefault01):
        self.attrdefault01 = attrdefault01
    def get_attrdefault02(self):
        return self.attrdefault02
    def set_attrdefault02(self, attrdefault02):
        self.attrdefault02 = attrdefault02
    def get_attrnormal01(self):
        return self.attrnormal01
    def set_attrnormal01(self, attrnormal01):
        self.attrnormal01 = attrnormal01
    def get_attrnormal02(self):
        return self.attrnormal02
    def set_attrnormal02(self, attrnormal02):
        self.attrnormal02 = attrnormal02
    def _hasContent(self):
        if (

        ):
            return True
        else:
            return False
    def export(self, outfile, level, namespaceprefix_='', namespacedef_='', name_='DefaultType2', pretty_print=True):
        imported_ns_def_ = GenerateDSNamespaceDefs_.get('DefaultType2')
        if imported_ns_def_ is not None:
            namespacedef_ = imported_ns_def_
        if pretty_print:
            eol_ = '\n'
        else:
            eol_ = ''
        if self.original_tagname_ is not None and name_ == 'DefaultType2':
            name_ = self.original_tagname_
        if UseCapturedNS_ and self.ns_prefix_:
            namespaceprefix_ = self.ns_prefix_ + ':'
        showIndent(outfile, level, pretty_print)
        outfile.write('<%s%s%s' % (namespaceprefix_, name_, namespacedef_ and ' ' + namespacedef_ or '', ))
        already_processed = set()
        self._exportAttributes(outfile, level, already_processed, namespaceprefix_, name_='DefaultType2')
        if self._hasContent():
            outfile.write('>%s' % (eol_, ))
            self._exportChildren(outfile, level + 1, namespaceprefix_, namespacedef_, name_='DefaultType2', pretty_print=pretty_print)
            outfile.write('</%s%s>%s' % (namespaceprefix_, name_, eol_))
        else:
            outfile.write('/>%s' % (eol_, ))
    def _exportAttributes(self, outfile, level, already_processed, namespaceprefix_='', name_='DefaultType2'):
        if self.attrdefault01 != "abcd" and 'attrdefault01' not in already_processed:
            already_processed.add('attrdefault01')
            outfile.write(' attrdefault01=%s' % (self.gds_encode(self.gds_format_string(quote_attrib(self.attrdefault01), input_name='attrdefault01')), ))
        if self.attrdefault02 != 14 and 'attrdefault02' not in already_processed:
            already_processed.add('attrdefault02')
            outfile.write(' attrdefault02="%s"' % self.gds_format_integer(self.attrdefault02, input_name='attrdefault02'))
        if self.attrnormal01 is not None and 'attrnormal01' not in already_processed:
            already_processed.add('attrnormal01')
            outfile.write(' attrnormal01=%s' % (self.gds_encode(self.gds_format_string(quote_attrib(self.attrnormal01), input_name='attrnormal01')), ))
        if self.attrnormal02 is not None and 'attrnormal02' not in already_processed:
            already_processed.add('attrnormal02')
            outfile.write(' attrnormal02="%s"' % self.gds_format_integer(self.attrnormal02, input_name='attrnormal02'))
    def _exportChildren(self, outfile, level, namespaceprefix_='', namespacedef_='', name_='DefaultType2', fromsubclass_=False, pretty_print=True):
        pass
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
        value = find_attr_value_('attrdefault01', node)
        if value is not None and 'attrdefault01' not in already_processed:
            already_processed.add('attrdefault01')
            self.attrdefault01 = value
        value = find_attr_value_('attrdefault02', node)
        if value is not None and 'attrdefault02' not in already_processed:
            already_processed.add('attrdefault02')
            self.attrdefault02 = self.gds_parse_integer(value, node, 'attrdefault02')
        value = find_attr_value_('attrnormal01', node)
        if value is not None and 'attrnormal01' not in already_processed:
            already_processed.add('attrnormal01')
            self.attrnormal01 = value
        value = find_attr_value_('attrnormal02', node)
        if value is not None and 'attrnormal02' not in already_processed:
            already_processed.add('attrnormal02')
            self.attrnormal02 = self.gds_parse_integer(value, node, 'attrnormal02')
    def _buildChildren(self, child_, node, nodeName_, fromsubclass_=False, gds_collector_=None):
        pass
# end class DefaultType2


class FixedType1(GeneratedsSuper):
    __hash__ = GeneratedsSuper.__hash__
    member_data_items_ = [
        MemberSpec_('normal01', 'xs:integer', 0, 1, {'minOccurs': '0', 'name': 'normal01', 'type': 'xs:integer'}, None),
        MemberSpec_('normal02', 'xs:string', 0, 1, {'minOccurs': '0', 'name': 'normal02', 'type': 'xs:string'}, None),
        MemberSpec_('fixed01', 'xs:integer', 0, 1, {'fixed': '23', 'minOccurs': '0', 'name': 'fixed01', 'type': 'xs:integer'}, None),
        MemberSpec_('fixed02', 'xs:string', 0, 1, {'fixed': 'Peach', 'minOccurs': '0', 'name': 'fixed02', 'type': 'xs:string'}, None),
        MemberSpec_('normal03', 'xs:float', 0, 0, {'minOccurs': '1', 'name': 'normal03', 'type': 'xs:float'}, None),
        MemberSpec_('normal04', 'xs:double', 0, 0, {'minOccurs': '1', 'name': 'normal04', 'type': 'xs:double'}, None),
        MemberSpec_('fixed03', 'xs:float', 0, 0, {'fixed': '23.45', 'minOccurs': '1', 'name': 'fixed03', 'type': 'xs:float'}, None),
        MemberSpec_('fixed04', 'xs:double', 0, 0, {'fixed': '54.32', 'minOccurs': '1', 'name': 'fixed04', 'type': 'xs:double'}, None),
    ]
    subclass = None
    superclass = None
    def __init__(self, normal01=None, normal02=None, fixed01=None, fixed02=None, normal03=None, normal04=None, fixed03=None, fixed04=None, gds_collector_=None, **kwargs_):
        self.gds_collector_ = gds_collector_
        self.gds_elementtree_node_ = None
        self.original_tagname_ = None
        self.parent_object_ = kwargs_.get('parent_object_')
        self.ns_prefix_ = None
        self.normal01 = normal01
        self.normal01_nsprefix_ = None
        self.normal02 = normal02
        self.normal02_nsprefix_ = None
        self.fixed01 = fixed01
        self.fixed01_nsprefix_ = None
        self.fixed02 = fixed02
        self.fixed02_nsprefix_ = None
        self.normal03 = normal03
        self.normal03_nsprefix_ = None
        self.normal04 = normal04
        self.normal04_nsprefix_ = None
        self.fixed03 = fixed03
        self.fixed03_nsprefix_ = None
        self.fixed04 = fixed04
        self.fixed04_nsprefix_ = None
    def factory(*args_, **kwargs_):
        if CurrentSubclassModule_ is not None:
            subclass = getSubclassFromModule_(
                CurrentSubclassModule_, FixedType1)
            if subclass is not None:
                return subclass(*args_, **kwargs_)
        if FixedType1.subclass:
            return FixedType1.subclass(*args_, **kwargs_)
        else:
            return FixedType1(*args_, **kwargs_)
    factory = staticmethod(factory)
    def get_ns_prefix_(self):
        return self.ns_prefix_
    def set_ns_prefix_(self, ns_prefix):
        self.ns_prefix_ = ns_prefix
    def get_normal01(self):
        return self.normal01
    def set_normal01(self, normal01):
        self.normal01 = normal01
    def get_normal02(self):
        return self.normal02
    def set_normal02(self, normal02):
        self.normal02 = normal02
    def get_fixed01(self):
        return self.fixed01
    def set_fixed01(self, fixed01):
        self.fixed01 = fixed01
    def get_fixed02(self):
        return self.fixed02
    def set_fixed02(self, fixed02):
        self.fixed02 = fixed02
    def get_normal03(self):
        return self.normal03
    def set_normal03(self, normal03):
        self.normal03 = normal03
    def get_normal04(self):
        return self.normal04
    def set_normal04(self, normal04):
        self.normal04 = normal04
    def get_fixed03(self):
        return self.fixed03
    def set_fixed03(self, fixed03):
        self.fixed03 = fixed03
    def get_fixed04(self):
        return self.fixed04
    def set_fixed04(self, fixed04):
        self.fixed04 = fixed04
    def _hasContent(self):
        if (
            self.normal01 is not None or
            self.normal02 is not None or
            self.fixed01 is not None or
            self.fixed02 is not None or
            self.normal03 is not None or
            self.normal04 is not None or
            self.fixed03 is not None or
            self.fixed04 is not None
        ):
            return True
        else:
            return False
    def export(self, outfile, level, namespaceprefix_='', namespacedef_='', name_='FixedType1', pretty_print=True):
        imported_ns_def_ = GenerateDSNamespaceDefs_.get('FixedType1')
        if imported_ns_def_ is not None:
            namespacedef_ = imported_ns_def_
        if pretty_print:
            eol_ = '\n'
        else:
            eol_ = ''
        if self.original_tagname_ is not None and name_ == 'FixedType1':
            name_ = self.original_tagname_
        if UseCapturedNS_ and self.ns_prefix_:
            namespaceprefix_ = self.ns_prefix_ + ':'
        showIndent(outfile, level, pretty_print)
        outfile.write('<%s%s%s' % (namespaceprefix_, name_, namespacedef_ and ' ' + namespacedef_ or '', ))
        already_processed = set()
        self._exportAttributes(outfile, level, already_processed, namespaceprefix_, name_='FixedType1')
        if self._hasContent():
            outfile.write('>%s' % (eol_, ))
            self._exportChildren(outfile, level + 1, namespaceprefix_, namespacedef_, name_='FixedType1', pretty_print=pretty_print)
            showIndent(outfile, level, pretty_print)
            outfile.write('</%s%s>%s' % (namespaceprefix_, name_, eol_))
        else:
            outfile.write('/>%s' % (eol_, ))
    def _exportAttributes(self, outfile, level, already_processed, namespaceprefix_='', name_='FixedType1'):
        pass
    def _exportChildren(self, outfile, level, namespaceprefix_='', namespacedef_='', name_='FixedType1', fromsubclass_=False, pretty_print=True):
        if pretty_print:
            eol_ = '\n'
        else:
            eol_ = ''
        if self.normal01 is not None:
            namespaceprefix_ = self.normal01_nsprefix_ + ':' if (UseCapturedNS_ and self.normal01_nsprefix_) else ''
            showIndent(outfile, level, pretty_print)
            outfile.write('<%snormal01>%s</%snormal01>%s' % (namespaceprefix_ , self.gds_format_integer(self.normal01, input_name='normal01'), namespaceprefix_ , eol_))
        if self.normal02 is not None:
            namespaceprefix_ = self.normal02_nsprefix_ + ':' if (UseCapturedNS_ and self.normal02_nsprefix_) else ''
            showIndent(outfile, level, pretty_print)
            outfile.write('<%snormal02>%s</%snormal02>%s' % (namespaceprefix_ , self.gds_encode(self.gds_format_string(quote_xml(self.normal02), input_name='normal02')), namespaceprefix_ , eol_))
        if self.fixed01 is not None:
            namespaceprefix_ = self.fixed01_nsprefix_ + ':' if (UseCapturedNS_ and self.fixed01_nsprefix_) else ''
            showIndent(outfile, level, pretty_print)
            outfile.write('<%sfixed01>%s</%sfixed01>%s' % (namespaceprefix_ , self.gds_format_integer(self.fixed01, input_name='fixed01'), namespaceprefix_ , eol_))
        if self.fixed02 is not None:
            namespaceprefix_ = self.fixed02_nsprefix_ + ':' if (UseCapturedNS_ and self.fixed02_nsprefix_) else ''
            showIndent(outfile, level, pretty_print)
            outfile.write('<%sfixed02>%s</%sfixed02>%s' % (namespaceprefix_ , self.gds_encode(self.gds_format_string(quote_xml(self.fixed02), input_name='fixed02')), namespaceprefix_ , eol_))
        if self.normal03 is not None:
            namespaceprefix_ = self.normal03_nsprefix_ + ':' if (UseCapturedNS_ and self.normal03_nsprefix_) else ''
            showIndent(outfile, level, pretty_print)
            outfile.write('<%snormal03>%s</%snormal03>%s' % (namespaceprefix_ , self.gds_format_float(self.normal03, input_name='normal03'), namespaceprefix_ , eol_))
        if self.normal04 is not None:
            namespaceprefix_ = self.normal04_nsprefix_ + ':' if (UseCapturedNS_ and self.normal04_nsprefix_) else ''
            showIndent(outfile, level, pretty_print)
            outfile.write('<%snormal04>%s</%snormal04>%s' % (namespaceprefix_ , self.gds_format_double(self.normal04, input_name='normal04'), namespaceprefix_ , eol_))
        if self.fixed03 is not None:
            namespaceprefix_ = self.fixed03_nsprefix_ + ':' if (UseCapturedNS_ and self.fixed03_nsprefix_) else ''
            showIndent(outfile, level, pretty_print)
            outfile.write('<%sfixed03>%s</%sfixed03>%s' % (namespaceprefix_ , self.gds_format_float(self.fixed03, input_name='fixed03'), namespaceprefix_ , eol_))
        if self.fixed04 is not None:
            namespaceprefix_ = self.fixed04_nsprefix_ + ':' if (UseCapturedNS_ and self.fixed04_nsprefix_) else ''
            showIndent(outfile, level, pretty_print)
            outfile.write('<%sfixed04>%s</%sfixed04>%s' % (namespaceprefix_ , self.gds_format_double(self.fixed04, input_name='fixed04'), namespaceprefix_ , eol_))
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
        if nodeName_ == 'normal01' and child_.text:
            sval_ = child_.text
            ival_ = self.gds_parse_integer(sval_, node, 'normal01')
            ival_ = self.gds_validate_integer(ival_, node, 'normal01')
            self.normal01 = ival_
            self.normal01_nsprefix_ = child_.prefix
        elif nodeName_ == 'normal02':
            value_ = child_.text
            value_ = self.gds_parse_string(value_, node, 'normal02')
            value_ = self.gds_validate_string(value_, node, 'normal02')
            self.normal02 = value_
            self.normal02_nsprefix_ = child_.prefix
        elif nodeName_ == 'fixed01' and child_.text:
            sval_ = child_.text
            ival_ = self.gds_parse_integer(sval_, node, 'fixed01')
            ival_ = self.gds_validate_integer(ival_, node, 'fixed01')
            self.fixed01 = ival_
            self.fixed01_nsprefix_ = child_.prefix
        elif nodeName_ == 'fixed02':
            value_ = child_.text
            value_ = self.gds_parse_string(value_, node, 'fixed02')
            value_ = self.gds_validate_string(value_, node, 'fixed02')
            self.fixed02 = value_
            self.fixed02_nsprefix_ = child_.prefix
        elif nodeName_ == 'normal03' and child_.text:
            sval_ = child_.text
            fval_ = self.gds_parse_float(sval_, node, 'normal03')
            fval_ = self.gds_validate_float(fval_, node, 'normal03')
            self.normal03 = fval_
            self.normal03_nsprefix_ = child_.prefix
        elif nodeName_ == 'normal04' and child_.text:
            sval_ = child_.text
            fval_ = self.gds_parse_double(sval_, node, 'normal04')
            fval_ = self.gds_validate_double(fval_, node, 'normal04')
            self.normal04 = fval_
            self.normal04_nsprefix_ = child_.prefix
        elif nodeName_ == 'fixed03' and child_.text:
            sval_ = child_.text
            fval_ = self.gds_parse_float(sval_, node, 'fixed03')
            fval_ = self.gds_validate_float(fval_, node, 'fixed03')
            self.fixed03 = fval_
            self.fixed03_nsprefix_ = child_.prefix
        elif nodeName_ == 'fixed04' and child_.text:
            sval_ = child_.text
            fval_ = self.gds_parse_double(sval_, node, 'fixed04')
            fval_ = self.gds_validate_double(fval_, node, 'fixed04')
            self.fixed04 = fval_
            self.fixed04_nsprefix_ = child_.prefix
# end class FixedType1


class FixedType2(GeneratedsSuper):
    __hash__ = GeneratedsSuper.__hash__
    member_data_items_ = [
        MemberSpec_('attrfixed01', 'xs:string', 0, 1, {'use': 'optional', 'name': 'attrfixed01'}),
        MemberSpec_('attrfixed02', 'xs:integer', 0, 1, {'use': 'optional', 'name': 'attrfixed02'}),
        MemberSpec_('attrnormal01', 'xs:string', 0, 1, {'use': 'optional', 'name': 'attrnormal01'}),
        MemberSpec_('attrnormal02', 'xs:integer', 0, 1, {'use': 'optional', 'name': 'attrnormal02'}),
    ]
    subclass = None
    superclass = None
    def __init__(self, attrfixed01='abcd', attrfixed02=14, attrnormal01=None, attrnormal02=None, gds_collector_=None, **kwargs_):
        self.gds_collector_ = gds_collector_
        self.gds_elementtree_node_ = None
        self.original_tagname_ = None
        self.parent_object_ = kwargs_.get('parent_object_')
        self.ns_prefix_ = None
        self.attrfixed01 = _cast(None, attrfixed01)
        self.attrfixed01_nsprefix_ = None
        self.attrfixed02 = _cast(int, attrfixed02)
        self.attrfixed02_nsprefix_ = None
        self.attrnormal01 = _cast(None, attrnormal01)
        self.attrnormal01_nsprefix_ = None
        self.attrnormal02 = _cast(int, attrnormal02)
        self.attrnormal02_nsprefix_ = None
    def factory(*args_, **kwargs_):
        if CurrentSubclassModule_ is not None:
            subclass = getSubclassFromModule_(
                CurrentSubclassModule_, FixedType2)
            if subclass is not None:
                return subclass(*args_, **kwargs_)
        if FixedType2.subclass:
            return FixedType2.subclass(*args_, **kwargs_)
        else:
            return FixedType2(*args_, **kwargs_)
    factory = staticmethod(factory)
    def get_ns_prefix_(self):
        return self.ns_prefix_
    def set_ns_prefix_(self, ns_prefix):
        self.ns_prefix_ = ns_prefix
    def get_attrfixed01(self):
        return self.attrfixed01
    def set_attrfixed01(self, attrfixed01):
        self.attrfixed01 = attrfixed01
    def get_attrfixed02(self):
        return self.attrfixed02
    def set_attrfixed02(self, attrfixed02):
        self.attrfixed02 = attrfixed02
    def get_attrnormal01(self):
        return self.attrnormal01
    def set_attrnormal01(self, attrnormal01):
        self.attrnormal01 = attrnormal01
    def get_attrnormal02(self):
        return self.attrnormal02
    def set_attrnormal02(self, attrnormal02):
        self.attrnormal02 = attrnormal02
    def _hasContent(self):
        if (

        ):
            return True
        else:
            return False
    def export(self, outfile, level, namespaceprefix_='', namespacedef_='', name_='FixedType2', pretty_print=True):
        imported_ns_def_ = GenerateDSNamespaceDefs_.get('FixedType2')
        if imported_ns_def_ is not None:
            namespacedef_ = imported_ns_def_
        if pretty_print:
            eol_ = '\n'
        else:
            eol_ = ''
        if self.original_tagname_ is not None and name_ == 'FixedType2':
            name_ = self.original_tagname_
        if UseCapturedNS_ and self.ns_prefix_:
            namespaceprefix_ = self.ns_prefix_ + ':'
        showIndent(outfile, level, pretty_print)
        outfile.write('<%s%s%s' % (namespaceprefix_, name_, namespacedef_ and ' ' + namespacedef_ or '', ))
        already_processed = set()
        self._exportAttributes(outfile, level, already_processed, namespaceprefix_, name_='FixedType2')
        if self._hasContent():
            outfile.write('>%s' % (eol_, ))
            self._exportChildren(outfile, level + 1, namespaceprefix_, namespacedef_, name_='FixedType2', pretty_print=pretty_print)
            outfile.write('</%s%s>%s' % (namespaceprefix_, name_, eol_))
        else:
            outfile.write('/>%s' % (eol_, ))
    def _exportAttributes(self, outfile, level, already_processed, namespaceprefix_='', name_='FixedType2'):
        if self.attrfixed01 != "abcd" and 'attrfixed01' not in already_processed:
            already_processed.add('attrfixed01')
            outfile.write(' attrfixed01=%s' % (self.gds_encode(self.gds_format_string(quote_attrib(self.attrfixed01), input_name='attrfixed01')), ))
        if self.attrfixed02 != 14 and 'attrfixed02' not in already_processed:
            already_processed.add('attrfixed02')
            outfile.write(' attrfixed02="%s"' % self.gds_format_integer(self.attrfixed02, input_name='attrfixed02'))
        if self.attrnormal01 is not None and 'attrnormal01' not in already_processed:
            already_processed.add('attrnormal01')
            outfile.write(' attrnormal01=%s' % (self.gds_encode(self.gds_format_string(quote_attrib(self.attrnormal01), input_name='attrnormal01')), ))
        if self.attrnormal02 is not None and 'attrnormal02' not in already_processed:
            already_processed.add('attrnormal02')
            outfile.write(' attrnormal02="%s"' % self.gds_format_integer(self.attrnormal02, input_name='attrnormal02'))
    def _exportChildren(self, outfile, level, namespaceprefix_='', namespacedef_='', name_='FixedType2', fromsubclass_=False, pretty_print=True):
        pass
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
        value = find_attr_value_('attrfixed01', node)
        if value is not None and 'attrfixed01' not in already_processed:
            already_processed.add('attrfixed01')
            self.attrfixed01 = value
        value = find_attr_value_('attrfixed02', node)
        if value is not None and 'attrfixed02' not in already_processed:
            already_processed.add('attrfixed02')
            self.attrfixed02 = self.gds_parse_integer(value, node, 'attrfixed02')
        value = find_attr_value_('attrnormal01', node)
        if value is not None and 'attrnormal01' not in already_processed:
            already_processed.add('attrnormal01')
            self.attrnormal01 = value
        value = find_attr_value_('attrnormal02', node)
        if value is not None and 'attrnormal02' not in already_processed:
            already_processed.add('attrnormal02')
            self.attrnormal02 = self.gds_parse_integer(value, node, 'attrnormal02')
    def _buildChildren(self, child_, node, nodeName_, fromsubclass_=False, gds_collector_=None):
        pass
# end class FixedType2


GDSClassesMapping = {
    'defaults': DefaultTypes,
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
        rootTag = 'DefaultTypes'
        rootClass = DefaultTypes
    rootObj = rootClass.factory()
    rootObj.build(rootNode, gds_collector_=gds_collector)
    CapturedNsmap_, namespacedefs = get_required_ns_prefix_defs(rootNode)
    if not SaveElementTreeNode:
        doc = None
        rootNode = None
    if not silence:
        sys.stdout.write('<?xml version="1.0" ?>\n')
        rootObj.export(
            sys.stdout, 0, name_=rootTag,
            namespacedef_=namespacedefs,
            pretty_print=True)
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
        rootTag = 'DefaultTypes'
        rootClass = DefaultTypes
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
    if not silence:
        content = etree_.tostring(
            rootElement, pretty_print=True,
            xml_declaration=True, encoding="utf-8")
        sys.stdout.write(str(content))
        sys.stdout.write('\n')
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
        rootTag = 'DefaultTypes'
        rootClass = DefaultTypes
    rootObj = rootClass.factory()
    rootObj.build(rootNode, gds_collector_=gds_collector)
    if not SaveElementTreeNode:
        rootNode = None
    if not silence:
        sys.stdout.write('<?xml version="1.0" ?>\n')
        rootObj.export(
            sys.stdout, 0, name_=rootTag,
            namespacedef_='')
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
        rootTag = 'DefaultTypes'
        rootClass = DefaultTypes
    rootObj = rootClass.factory()
    rootObj.build(rootNode, gds_collector_=gds_collector)
    # Enable Python to collect the space used by the DOM.
    if not SaveElementTreeNode:
        doc = None
        rootNode = None
    if not silence:
        sys.stdout.write('#from defaults_cases2_sup import *\n\n')
        sys.stdout.write('import defaults_cases2_sup as model_\n\n')
        sys.stdout.write('rootObj = model_.rootClass(\n')
        rootObj.exportLiteral(sys.stdout, 0, name_=rootTag)
        sys.stdout.write(')\n')
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
    "DefaultType1",
    "DefaultType2",
    "DefaultTypes",
    "FixedType1",
    "FixedType2"
]
