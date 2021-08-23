#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# Generated  by generateDS.py.
# Python 3.8.11 (default, Aug  3 2021, 15:09:35)  [GCC 7.5.0]
#
# Command line options:
#   ('--no-dates', '')
#   ('--no-versions', '')
#   ('-f', '')
#   ('-o', 'tests/out2_sup.py')
#   ('-s', 'tests/out2_sub.py')
#   ('--export', 'write literal')
#   ('--super', 'out2_sup')
#   ('-u', 'gends_user_methods.py')
#
# Command line arguments:
#   tests/people.xsd
#
# Command line:
#   generateDS.py --no-dates --no-versions -f -o "tests/out2_sup.py" -s "tests/out2_sub.py" --export="write literal" --super="out2_sup" -u "gends_user_methods.py" tests/people.xsd
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


class people(GeneratedsSuper):
    __hash__ = GeneratedsSuper.__hash__
    member_data_items_ = [
        MemberSpec_('comments', 'comments', 1, 0, {'maxOccurs': 'unbounded', 'name': 'comments', 'type': 'comments'}, None),
        MemberSpec_('person', 'person', 1, 0, {'maxOccurs': 'unbounded', 'name': 'person', 'type': 'person'}, None),
        MemberSpec_('programmer', 'programmer', 1, 0, {'maxOccurs': 'unbounded', 'name': 'programmer', 'type': 'programmer'}, None),
        MemberSpec_('python_programmer', 'python-programmer', 1, 0, {'maxOccurs': 'unbounded', 'name': 'python-programmer', 'type': 'python-programmer'}, None),
        MemberSpec_('java_programmer', 'java-programmer', 1, 0, {'maxOccurs': 'unbounded', 'name': 'java-programmer', 'type': 'java-programmer'}, None),
    ]
    subclass = None
    superclass = None
    def __init__(self, comments=None, person=None, programmer=None, python_programmer=None, java_programmer=None, gds_collector_=None, **kwargs_):
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
                CurrentSubclassModule_, people)
            if subclass is not None:
                return subclass(*args_, **kwargs_)
        if people.subclass:
            return people.subclass(*args_, **kwargs_)
        else:
            return people(*args_, **kwargs_)
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
            self.programmer or
            self.python_programmer or
            self.java_programmer
        ):
            return True
        else:
            return False
    def export(self, outfile, level, namespaceprefix_='', namespacedef_='', name_='people', pretty_print=True):
        imported_ns_def_ = GenerateDSNamespaceDefs_.get('people')
        if imported_ns_def_ is not None:
            namespacedef_ = imported_ns_def_
        if pretty_print:
            eol_ = '\n'
        else:
            eol_ = ''
        if self.original_tagname_ is not None and name_ == 'people':
            name_ = self.original_tagname_
        if UseCapturedNS_ and self.ns_prefix_:
            namespaceprefix_ = self.ns_prefix_ + ':'
        showIndent(outfile, level, pretty_print)
        outfile.write('<%s%s%s' % (namespaceprefix_, name_, namespacedef_ and ' ' + namespacedef_ or '', ))
        already_processed = set()
        self._exportAttributes(outfile, level, already_processed, namespaceprefix_, name_='people')
        if self._hasContent():
            outfile.write('>%s' % (eol_, ))
            self._exportChildren(outfile, level + 1, namespaceprefix_, namespacedef_, name_='people', pretty_print=pretty_print)
            showIndent(outfile, level, pretty_print)
            outfile.write('</%s%s>%s' % (namespaceprefix_, name_, eol_))
        else:
            outfile.write('/>%s' % (eol_, ))
    def _exportAttributes(self, outfile, level, already_processed, namespaceprefix_='', name_='people'):
        pass
    def _exportChildren(self, outfile, level, namespaceprefix_='', namespacedef_='', name_='people', fromsubclass_=False, pretty_print=True):
        if pretty_print:
            eol_ = '\n'
        else:
            eol_ = ''
        for comments_ in self.comments:
            namespaceprefix_ = self.comments_nsprefix_ + ':' if (UseCapturedNS_ and self.comments_nsprefix_) else ''
            comments_.export(outfile, level, namespaceprefix_, namespacedef_='', name_='comments', pretty_print=pretty_print)
        for person_ in self.person:
            namespaceprefix_ = self.person_nsprefix_ + ':' if (UseCapturedNS_ and self.person_nsprefix_) else ''
            person_.export(outfile, level, namespaceprefix_, namespacedef_='', name_='person', pretty_print=pretty_print)
        for programmer_ in self.programmer:
            namespaceprefix_ = self.programmer_nsprefix_ + ':' if (UseCapturedNS_ and self.programmer_nsprefix_) else ''
            programmer_.export(outfile, level, namespaceprefix_, namespacedef_='', name_='programmer', pretty_print=pretty_print)
        for python_programmer_ in self.python_programmer:
            namespaceprefix_ = self.python_programmer_nsprefix_ + ':' if (UseCapturedNS_ and self.python_programmer_nsprefix_) else ''
            python_programmer_.export(outfile, level, namespaceprefix_, namespacedef_='', name_='python-programmer', pretty_print=pretty_print)
        for java_programmer_ in self.java_programmer:
            namespaceprefix_ = self.java_programmer_nsprefix_ + ':' if (UseCapturedNS_ and self.java_programmer_nsprefix_) else ''
            java_programmer_.export(outfile, level, namespaceprefix_, namespacedef_='', name_='java-programmer', pretty_print=pretty_print)
    def exportLiteral(self, outfile, level, name_='people'):
        level += 1
        already_processed = set()
        self._exportLiteralAttributes(outfile, level, already_processed, name_)
        if self._hasContent():
            self._exportLiteralChildren(outfile, level, name_)
    def _exportLiteralAttributes(self, outfile, level, already_processed, name_):
        pass
    def _exportLiteralChildren(self, outfile, level, name_):
        showIndent(outfile, level)
        outfile.write('comments=[\n')
        level += 1
        for comments_ in self.comments:
            showIndent(outfile, level)
            outfile.write('model_.comments(\n')
            comments_.exportLiteral(outfile, level)
            showIndent(outfile, level)
            outfile.write('),\n')
        level -= 1
        showIndent(outfile, level)
        outfile.write('],\n')
        showIndent(outfile, level)
        outfile.write('person=[\n')
        level += 1
        for person_ in self.person:
            showIndent(outfile, level)
            outfile.write('model_.person(\n')
            person_.exportLiteral(outfile, level)
            showIndent(outfile, level)
            outfile.write('),\n')
        level -= 1
        showIndent(outfile, level)
        outfile.write('],\n')
        showIndent(outfile, level)
        outfile.write('programmer=[\n')
        level += 1
        for programmer_ in self.programmer:
            showIndent(outfile, level)
            outfile.write('model_.programmer(\n')
            programmer_.exportLiteral(outfile, level)
            showIndent(outfile, level)
            outfile.write('),\n')
        level -= 1
        showIndent(outfile, level)
        outfile.write('],\n')
        showIndent(outfile, level)
        outfile.write('python_programmer=[\n')
        level += 1
        for python_programmer_ in self.python_programmer:
            showIndent(outfile, level)
            outfile.write('model_.python_programmer(\n')
            python_programmer_.exportLiteral(outfile, level, name_='python-programmer')
            showIndent(outfile, level)
            outfile.write('),\n')
        level -= 1
        showIndent(outfile, level)
        outfile.write('],\n')
        showIndent(outfile, level)
        outfile.write('java_programmer=[\n')
        level += 1
        for java_programmer_ in self.java_programmer:
            showIndent(outfile, level)
            outfile.write('model_.java_programmer(\n')
            java_programmer_.exportLiteral(outfile, level, name_='java-programmer')
            showIndent(outfile, level)
            outfile.write('),\n')
        level -= 1
        showIndent(outfile, level)
        outfile.write('],\n')
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
            obj_ = comments.factory(parent_object_=self)
            obj_.build(child_, gds_collector_=gds_collector_)
            self.comments.append(obj_)
            obj_.original_tagname_ = 'comments'
        elif nodeName_ == 'person':
            class_obj_ = self.get_class_obj_(child_, person)
            obj_ = class_obj_.factory(parent_object_=self)
            obj_.build(child_, gds_collector_=gds_collector_)
            self.person.append(obj_)
            obj_.original_tagname_ = 'person'
        elif nodeName_ == 'programmer':
            class_obj_ = self.get_class_obj_(child_, programmer)
            obj_ = class_obj_.factory(parent_object_=self)
            obj_.build(child_, gds_collector_=gds_collector_)
            self.programmer.append(obj_)
            obj_.original_tagname_ = 'programmer'
        elif nodeName_ == 'python-programmer':
            obj_ = python_programmer.factory(parent_object_=self)
            obj_.build(child_, gds_collector_=gds_collector_)
            self.python_programmer.append(obj_)
            obj_.original_tagname_ = 'python-programmer'
        elif nodeName_ == 'java-programmer':
            obj_ = java_programmer.factory(parent_object_=self)
            obj_.build(child_, gds_collector_=gds_collector_)
            self.java_programmer.append(obj_)
            obj_.original_tagname_ = 'java-programmer'
    def walk_and_update(self):
        members = people._member_data_items
        for member in members:
            obj1 = getattr(self, member.get_name())
            if member.get_data_type() == 'xs:date':
                newvalue = date_calcs.date_from_string(obj1)
                setattr(self, member.get_name(), newvalue)
            elif member.get_container():
                for child in obj1:
                    if type(child) == types.InstanceType:
                        child.walk_and_update()
            else:
                obj1 = getattr(self, member.get_name())
                if type(obj1) == types.InstanceType:
                    obj1.walk_and_update()
        if people.superclass != None:
          people.superclass.walk_and_update(self)
    def walk_and_show(self, depth):
        global counter
        counter += 1
        depth += 1
        print('%d. class: people  depth: %d' % (counter, depth, ))
        members = people._member_data_items
        for member in members:
            s1 = member.get_name()
            s2 = member.get_data_type()
            s3 = '%d' % member.get_container()
            obj1 = getattr(self, member.get_name())
            if member.get_container():
                s4 = '<container>'
            else:
                if type(obj1) != types.InstanceType:
                    s4 = '%s' % obj1
                else:
                    s4 = '<instance>'
            s5 = '%s%s%s  %s' % (s1.ljust(16), s2.ljust(16), s3.rjust(4), s4, )
            print('   ', s5)
        for member in members:
            if member.get_container():
                for child in getattr(self, member.get_name()):
                    if type(child) == types.InstanceType:
                        child.walk_and_show(depth)
            else:
                obj1 = getattr(self, member.get_name())
                if type(obj1) == types.InstanceType:
                    obj1.walk_and_show(depth)
    def set_up(self):
        global types, counter
        import types as types_module
        types = types_module
        counter = 0
# end class people


class comments(GeneratedsSuper):
    __hash__ = GeneratedsSuper.__hash__
    member_data_items_ = [
        MemberSpec_('emp', 'xs:string', 1, 0, {'maxOccurs': 'unbounded', 'name': 'emp', 'type': 'xs:string'}, None),
        MemberSpec_('valueOf_', [], 0),
    ]
    subclass = None
    superclass = None
    def __init__(self, emp=None, valueOf_=None, mixedclass_=None, content_=None, gds_collector_=None, **kwargs_):
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
                CurrentSubclassModule_, comments)
            if subclass is not None:
                return subclass(*args_, **kwargs_)
        if comments.subclass:
            return comments.subclass(*args_, **kwargs_)
        else:
            return comments(*args_, **kwargs_)
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
    def get_valueOf_(self): return self.valueOf_
    def set_valueOf_(self, valueOf_): self.valueOf_ = valueOf_
    def _hasContent(self):
        if (
            self.emp or
            (1 if type(self.valueOf_) in [int,float] else self.valueOf_) or
            self.content_
        ):
            return True
        else:
            return False
    def export(self, outfile, level, namespaceprefix_='', namespacedef_='', name_='comments', pretty_print=True):
        imported_ns_def_ = GenerateDSNamespaceDefs_.get('comments')
        if imported_ns_def_ is not None:
            namespacedef_ = imported_ns_def_
        if pretty_print:
            eol_ = '\n'
        else:
            eol_ = ''
        if self.original_tagname_ is not None and name_ == 'comments':
            name_ = self.original_tagname_
        if UseCapturedNS_ and self.ns_prefix_:
            namespaceprefix_ = self.ns_prefix_ + ':'
        showIndent(outfile, level, pretty_print)
        outfile.write('<%s%s%s' % (namespaceprefix_, name_, namespacedef_ and ' ' + namespacedef_ or '', ))
        already_processed = set()
        self._exportAttributes(outfile, level, already_processed, namespaceprefix_, name_='comments')
        if self._hasContent():
            outfile.write('>%s' % (eol_, ))
            self._exportChildren(outfile, level + 1, namespaceprefix_, namespacedef_, name_='comments', pretty_print=pretty_print)
            showIndent(outfile, level, pretty_print)
            outfile.write('</%s%s>%s' % (namespaceprefix_, name_, eol_))
        else:
            outfile.write('/>%s' % (eol_, ))
    def _exportAttributes(self, outfile, level, already_processed, namespaceprefix_='', name_='comments'):
        pass
    def _exportChildren(self, outfile, level, namespaceprefix_='', namespacedef_='', name_='comments', fromsubclass_=False, pretty_print=True):
        if not fromsubclass_:
            for item_ in self.content_:
                item_.export(outfile, level, item_.name, namespaceprefix_, pretty_print=pretty_print)
        if pretty_print:
            eol_ = '\n'
        else:
            eol_ = ''
        for emp_ in self.emp:
            namespaceprefix_ = self.emp_nsprefix_ + ':' if (UseCapturedNS_ and self.emp_nsprefix_) else ''
            showIndent(outfile, level, pretty_print)
            outfile.write('<%semp>%s</%semp>%s' % (namespaceprefix_ , self.gds_encode(self.gds_format_string(quote_xml(emp_), input_name='emp')), namespaceprefix_ , eol_))
    def exportLiteral(self, outfile, level, name_='comments'):
        level += 1
        already_processed = set()
        self._exportLiteralAttributes(outfile, level, already_processed, name_)
        if self._hasContent():
            self._exportLiteralChildren(outfile, level, name_)
        showIndent(outfile, level)
        outfile.write('valueOf_ = """%s""",\n' % (self.valueOf_,))
    def _exportLiteralAttributes(self, outfile, level, already_processed, name_):
        pass
    def _exportLiteralChildren(self, outfile, level, name_):
        showIndent(outfile, level)
        outfile.write('content_ = [\n')
        for item_ in self.content_:
            item_.exportLiteral(outfile, level, name_)
        showIndent(outfile, level)
        outfile.write('],\n')
        pass
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
        if not fromsubclass_ and child_.tail is not None:
            obj_ = self.mixedclass_(MixedContainer.CategoryText,
                MixedContainer.TypeNone, '', child_.tail)
            self.content_.append(obj_)
    def walk_and_update(self):
        members = comments._member_data_items
        for member in members:
            obj1 = getattr(self, member.get_name())
            if member.get_data_type() == 'xs:date':
                newvalue = date_calcs.date_from_string(obj1)
                setattr(self, member.get_name(), newvalue)
            elif member.get_container():
                for child in obj1:
                    if type(child) == types.InstanceType:
                        child.walk_and_update()
            else:
                obj1 = getattr(self, member.get_name())
                if type(obj1) == types.InstanceType:
                    obj1.walk_and_update()
        if comments.superclass != None:
          comments.superclass.walk_and_update(self)
    def walk_and_show(self, depth):
        global counter
        counter += 1
        depth += 1
        print('%d. class: comments  depth: %d' % (counter, depth, ))
        members = comments._member_data_items
        for member in members:
            s1 = member.get_name()
            s2 = member.get_data_type()
            s3 = '%d' % member.get_container()
            obj1 = getattr(self, member.get_name())
            if member.get_container():
                s4 = '<container>'
            else:
                if type(obj1) != types.InstanceType:
                    s4 = '%s' % obj1
                else:
                    s4 = '<instance>'
            s5 = '%s%s%s  %s' % (s1.ljust(16), s2.ljust(16), s3.rjust(4), s4, )
            print('   ', s5)
        for member in members:
            if member.get_container():
                for child in getattr(self, member.get_name()):
                    if type(child) == types.InstanceType:
                        child.walk_and_show(depth)
            else:
                obj1 = getattr(self, member.get_name())
                if type(obj1) == types.InstanceType:
                    obj1.walk_and_show(depth)
# end class comments


class person(GeneratedsSuper):
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
        MemberSpec_('agent', 'agent', 1, 0, {'maxOccurs': 'unbounded', 'name': 'agent', 'type': 'agent'}, None),
        MemberSpec_('promoter', 'booster', 1, 0, {'maxOccurs': 'unbounded', 'name': 'promoter', 'type': 'booster'}, None),
        MemberSpec_('description', 'xs:string', 0, 0, {'name': 'description', 'type': 'xs:string'}, None),
    ]
    subclass = None
    superclass = None
    def __init__(self, value=None, id=None, ratio=None, fruit=None, vegetable=None, name=None, interest=None, category=None, agent=None, promoter=None, description=None, extensiontype_=None, gds_collector_=None, **kwargs_):
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
        self.extensiontype_ = extensiontype_
    def factory(*args_, **kwargs_):
        if CurrentSubclassModule_ is not None:
            subclass = getSubclassFromModule_(
                CurrentSubclassModule_, person)
            if subclass is not None:
                return subclass(*args_, **kwargs_)
        if person.subclass:
            return person.subclass(*args_, **kwargs_)
        else:
            return person(*args_, **kwargs_)
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
    def _hasContent(self):
        if (
            self.name is not None or
            self.interest or
            self.category is not None or
            self.agent or
            self.promoter or
            self.description is not None
        ):
            return True
        else:
            return False
    def export(self, outfile, level, namespaceprefix_='', namespacedef_='', name_='person', pretty_print=True):
        imported_ns_def_ = GenerateDSNamespaceDefs_.get('person')
        if imported_ns_def_ is not None:
            namespacedef_ = imported_ns_def_
        if pretty_print:
            eol_ = '\n'
        else:
            eol_ = ''
        if self.original_tagname_ is not None and name_ == 'person':
            name_ = self.original_tagname_
        if UseCapturedNS_ and self.ns_prefix_:
            namespaceprefix_ = self.ns_prefix_ + ':'
        showIndent(outfile, level, pretty_print)
        outfile.write('<%s%s%s' % (namespaceprefix_, name_, namespacedef_ and ' ' + namespacedef_ or '', ))
        already_processed = set()
        self._exportAttributes(outfile, level, already_processed, namespaceprefix_, name_='person')
        if self._hasContent():
            outfile.write('>%s' % (eol_, ))
            self._exportChildren(outfile, level + 1, namespaceprefix_, namespacedef_, name_='person', pretty_print=pretty_print)
            showIndent(outfile, level, pretty_print)
            outfile.write('</%s%s>%s' % (namespaceprefix_, name_, eol_))
        else:
            outfile.write('/>%s' % (eol_, ))
    def _exportAttributes(self, outfile, level, already_processed, namespaceprefix_='', name_='person'):
        if self.value is not None and 'value' not in already_processed:
            already_processed.add('value')
            outfile.write(' value=%s' % (self.gds_encode(self.gds_format_string(quote_attrib(self.value), input_name='value')), ))
        if self.id is not None and 'id' not in already_processed:
            already_processed.add('id')
            outfile.write(' id="%s"' % self.gds_format_integer(self.id, input_name='id'))
        if self.ratio is not None and 'ratio' not in already_processed:
            already_processed.add('ratio')
            outfile.write(' ratio="%s"' % self.gds_format_float(self.ratio, input_name='ratio'))
        if self.fruit is not None and 'fruit' not in already_processed:
            already_processed.add('fruit')
            outfile.write(' fruit=%s' % (self.gds_encode(self.gds_format_string(quote_attrib(self.fruit), input_name='fruit')), ))
        if self.vegetable is not None and 'vegetable' not in already_processed:
            already_processed.add('vegetable')
            outfile.write(' vegetable=%s' % (self.gds_encode(self.gds_format_string(quote_attrib(self.vegetable), input_name='vegetable')), ))
        if self.extensiontype_ is not None and 'xsi:type' not in already_processed:
            already_processed.add('xsi:type')
            outfile.write(' xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"')
            if ":" not in self.extensiontype_:
                imported_ns_type_prefix_ = GenerateDSNamespaceTypePrefixes_.get(self.extensiontype_, '')
                outfile.write(' xsi:type="%s%s"' % (imported_ns_type_prefix_, self.extensiontype_))
            else:
                outfile.write(' xsi:type="%s"' % self.extensiontype_)
    def _exportChildren(self, outfile, level, namespaceprefix_='', namespacedef_='', name_='person', fromsubclass_=False, pretty_print=True):
        if pretty_print:
            eol_ = '\n'
        else:
            eol_ = ''
        if self.name is not None:
            namespaceprefix_ = self.name_nsprefix_ + ':' if (UseCapturedNS_ and self.name_nsprefix_) else ''
            showIndent(outfile, level, pretty_print)
            outfile.write('<%sname>%s</%sname>%s' % (namespaceprefix_ , self.gds_encode(self.gds_format_string(quote_xml(self.name), input_name='name')), namespaceprefix_ , eol_))
        for interest_ in self.interest:
            namespaceprefix_ = self.interest_nsprefix_ + ':' if (UseCapturedNS_ and self.interest_nsprefix_) else ''
            showIndent(outfile, level, pretty_print)
            outfile.write('<%sinterest>%s</%sinterest>%s' % (namespaceprefix_ , self.gds_encode(self.gds_format_string(quote_xml(interest_), input_name='interest')), namespaceprefix_ , eol_))
        if self.category is not None:
            namespaceprefix_ = self.category_nsprefix_ + ':' if (UseCapturedNS_ and self.category_nsprefix_) else ''
            showIndent(outfile, level, pretty_print)
            outfile.write('<%scategory>%s</%scategory>%s' % (namespaceprefix_ , self.gds_format_integer(self.category, input_name='category'), namespaceprefix_ , eol_))
        for agent_ in self.agent:
            namespaceprefix_ = self.agent_nsprefix_ + ':' if (UseCapturedNS_ and self.agent_nsprefix_) else ''
            agent_.export(outfile, level, namespaceprefix_, namespacedef_='', name_='agent', pretty_print=pretty_print)
        for promoter_ in self.promoter:
            namespaceprefix_ = self.promoter_nsprefix_ + ':' if (UseCapturedNS_ and self.promoter_nsprefix_) else ''
            promoter_.export(outfile, level, namespaceprefix_, namespacedef_='', name_='promoter', pretty_print=pretty_print)
        if self.description is not None:
            namespaceprefix_ = self.description_nsprefix_ + ':' if (UseCapturedNS_ and self.description_nsprefix_) else ''
            showIndent(outfile, level, pretty_print)
            outfile.write('<%sdescription>%s</%sdescription>%s' % (namespaceprefix_ , self.gds_encode(self.gds_format_string(quote_xml(self.description), input_name='description')), namespaceprefix_ , eol_))
    def exportLiteral(self, outfile, level, name_='person'):
        level += 1
        already_processed = set()
        self._exportLiteralAttributes(outfile, level, already_processed, name_)
        if self._hasContent():
            self._exportLiteralChildren(outfile, level, name_)
    def _exportLiteralAttributes(self, outfile, level, already_processed, name_):
        if self.value is not None and 'value' not in already_processed:
            already_processed.add('value')
            showIndent(outfile, level)
            outfile.write('value="%s",\n' % (self.value,))
        if self.id is not None and 'id' not in already_processed:
            already_processed.add('id')
            showIndent(outfile, level)
            outfile.write('id=%d,\n' % (self.id,))
        if self.ratio is not None and 'ratio' not in already_processed:
            already_processed.add('ratio')
            showIndent(outfile, level)
            outfile.write('ratio=%f,\n' % (self.ratio,))
        if self.fruit is not None and 'fruit' not in already_processed:
            already_processed.add('fruit')
            showIndent(outfile, level)
            outfile.write('fruit="%s",\n' % (self.fruit,))
        if self.vegetable is not None and 'vegetable' not in already_processed:
            already_processed.add('vegetable')
            showIndent(outfile, level)
            outfile.write('vegetable="%s",\n' % (self.vegetable,))
    def _exportLiteralChildren(self, outfile, level, name_):
        if self.name is not None:
            showIndent(outfile, level)
            outfile.write('name=%s,\n' % self.gds_encode(quote_python(self.name)))
        showIndent(outfile, level)
        outfile.write('interest=[\n')
        level += 1
        for interest_ in self.interest:
            showIndent(outfile, level)
            outfile.write('%s,\n' % self.gds_encode(quote_python(interest_)))
        level -= 1
        showIndent(outfile, level)
        outfile.write('],\n')
        if self.category is not None:
            showIndent(outfile, level)
            outfile.write('category=%d,\n' % self.category)
        showIndent(outfile, level)
        outfile.write('agent=[\n')
        level += 1
        for agent_ in self.agent:
            showIndent(outfile, level)
            outfile.write('model_.agent(\n')
            agent_.exportLiteral(outfile, level)
            showIndent(outfile, level)
            outfile.write('),\n')
        level -= 1
        showIndent(outfile, level)
        outfile.write('],\n')
        showIndent(outfile, level)
        outfile.write('promoter=[\n')
        level += 1
        for promoter_ in self.promoter:
            showIndent(outfile, level)
            outfile.write('model_.booster(\n')
            promoter_.exportLiteral(outfile, level, name_='booster')
            showIndent(outfile, level)
            outfile.write('),\n')
        level -= 1
        showIndent(outfile, level)
        outfile.write('],\n')
        if self.description is not None:
            showIndent(outfile, level)
            outfile.write('description=%s,\n' % self.gds_encode(quote_python(self.description)))
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
        elif nodeName_ == 'agent':
            obj_ = agent.factory(parent_object_=self)
            obj_.build(child_, gds_collector_=gds_collector_)
            self.agent.append(obj_)
            obj_.original_tagname_ = 'agent'
        elif nodeName_ == 'promoter':
            obj_ = booster.factory(parent_object_=self)
            obj_.build(child_, gds_collector_=gds_collector_)
            self.promoter.append(obj_)
            obj_.original_tagname_ = 'promoter'
        elif nodeName_ == 'description':
            value_ = child_.text
            value_ = self.gds_parse_string(value_, node, 'description')
            value_ = self.gds_validate_string(value_, node, 'description')
            self.description = value_
            self.description_nsprefix_ = child_.prefix
    def walk_and_update(self):
        members = person._member_data_items
        for member in members:
            obj1 = getattr(self, member.get_name())
            if member.get_data_type() == 'xs:date':
                newvalue = date_calcs.date_from_string(obj1)
                setattr(self, member.get_name(), newvalue)
            elif member.get_container():
                for child in obj1:
                    if type(child) == types.InstanceType:
                        child.walk_and_update()
            else:
                obj1 = getattr(self, member.get_name())
                if type(obj1) == types.InstanceType:
                    obj1.walk_and_update()
        if person.superclass != None:
          person.superclass.walk_and_update(self)
    def walk_and_show(self, depth):
        global counter
        counter += 1
        depth += 1
        print('%d. class: person  depth: %d' % (counter, depth, ))
        members = person._member_data_items
        for member in members:
            s1 = member.get_name()
            s2 = member.get_data_type()
            s3 = '%d' % member.get_container()
            obj1 = getattr(self, member.get_name())
            if member.get_container():
                s4 = '<container>'
            else:
                if type(obj1) != types.InstanceType:
                    s4 = '%s' % obj1
                else:
                    s4 = '<instance>'
            s5 = '%s%s%s  %s' % (s1.ljust(16), s2.ljust(16), s3.rjust(4), s4, )
            print('   ', s5)
        for member in members:
            if member.get_container():
                for child in getattr(self, member.get_name()):
                    if type(child) == types.InstanceType:
                        child.walk_and_show(depth)
            else:
                obj1 = getattr(self, member.get_name())
                if type(obj1) == types.InstanceType:
                    obj1.walk_and_show(depth)
# end class person


class programmer(person):
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
        MemberSpec_('eltoken', 'xs:token', 0, 0, {'name': 'eltoken', 'type': 'xs:token'}, None),
        MemberSpec_('elshort', 'xs:short', 0, 0, {'name': 'elshort', 'type': 'xs:short'}, None),
        MemberSpec_('ellong', 'xs:long', 0, 0, {'name': 'ellong', 'type': 'xs:long'}, None),
        MemberSpec_('elparam', 'param', 0, 0, {'name': 'elparam', 'type': 'param'}, None),
        MemberSpec_('elarraytypes', ['ArrayTypes', 'xs:NMTOKEN'], 0, 0, {'name': 'elarraytypes', 'type': 'xs:NMTOKEN'}, None),
    ]
    subclass = None
    superclass = person
    def __init__(self, value=None, id=None, ratio=None, fruit=None, vegetable=None, name=None, interest=None, category=None, agent=None, promoter=None, description=None, language=None, area=None, attrposint=None, attrnonposint=None, attrnegint=None, attrnonnegint=None, email=None, elposint=None, elnonposint=None, elnegint=None, elnonnegint=None, eldate=None, eldatetime=None, eltoken=None, elshort=None, ellong=None, elparam=None, elarraytypes=None, extensiontype_=None, gds_collector_=None, **kwargs_):
        self.gds_collector_ = gds_collector_
        self.gds_elementtree_node_ = None
        self.original_tagname_ = None
        self.parent_object_ = kwargs_.get('parent_object_')
        self.ns_prefix_ = None
        super(globals().get("programmer"), self).__init__(value, id, ratio, fruit, vegetable, name, interest, category, agent, promoter, description, extensiontype_,  **kwargs_)
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
                CurrentSubclassModule_, programmer)
            if subclass is not None:
                return subclass(*args_, **kwargs_)
        if programmer.subclass:
            return programmer.subclass(*args_, **kwargs_)
        else:
            return programmer(*args_, **kwargs_)
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
            self.eltoken is not None or
            self.elshort is not None or
            self.ellong is not None or
            self.elparam is not None or
            self.elarraytypes is not None or
            super(programmer, self)._hasContent()
        ):
            return True
        else:
            return False
    def export(self, outfile, level, namespaceprefix_='', namespacedef_='', name_='programmer', pretty_print=True):
        imported_ns_def_ = GenerateDSNamespaceDefs_.get('programmer')
        if imported_ns_def_ is not None:
            namespacedef_ = imported_ns_def_
        if pretty_print:
            eol_ = '\n'
        else:
            eol_ = ''
        if self.original_tagname_ is not None and name_ == 'programmer':
            name_ = self.original_tagname_
        if UseCapturedNS_ and self.ns_prefix_:
            namespaceprefix_ = self.ns_prefix_ + ':'
        showIndent(outfile, level, pretty_print)
        outfile.write('<%s%s%s' % (namespaceprefix_, name_, namespacedef_ and ' ' + namespacedef_ or '', ))
        already_processed = set()
        self._exportAttributes(outfile, level, already_processed, namespaceprefix_, name_='programmer')
        if self._hasContent():
            outfile.write('>%s' % (eol_, ))
            self._exportChildren(outfile, level + 1, namespaceprefix_, namespacedef_, name_='programmer', pretty_print=pretty_print)
            showIndent(outfile, level, pretty_print)
            outfile.write('</%s%s>%s' % (namespaceprefix_, name_, eol_))
        else:
            outfile.write('/>%s' % (eol_, ))
    def _exportAttributes(self, outfile, level, already_processed, namespaceprefix_='', name_='programmer'):
        super(programmer, self)._exportAttributes(outfile, level, already_processed, namespaceprefix_, name_='programmer')
        if self.language is not None and 'language' not in already_processed:
            already_processed.add('language')
            outfile.write(' language=%s' % (self.gds_encode(self.gds_format_string(quote_attrib(self.language), input_name='language')), ))
        if self.area is not None and 'area' not in already_processed:
            already_processed.add('area')
            outfile.write(' area=%s' % (self.gds_encode(self.gds_format_string(quote_attrib(self.area), input_name='area')), ))
        if self.attrposint is not None and 'attrposint' not in already_processed:
            already_processed.add('attrposint')
            outfile.write(' attrposint="%s"' % self.gds_format_integer(self.attrposint, input_name='attrposint'))
        if self.attrnonposint is not None and 'attrnonposint' not in already_processed:
            already_processed.add('attrnonposint')
            outfile.write(' attrnonposint="%s"' % self.gds_format_integer(self.attrnonposint, input_name='attrnonposint'))
        if self.attrnegint is not None and 'attrnegint' not in already_processed:
            already_processed.add('attrnegint')
            outfile.write(' attrnegint="%s"' % self.gds_format_integer(self.attrnegint, input_name='attrnegint'))
        if self.attrnonnegint is not None and 'attrnonnegint' not in already_processed:
            already_processed.add('attrnonnegint')
            outfile.write(' attrnonnegint="%s"' % self.gds_format_integer(self.attrnonnegint, input_name='attrnonnegint'))
        if self.extensiontype_ is not None and 'xsi:type' not in already_processed:
            already_processed.add('xsi:type')
            outfile.write(' xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"')
            if ":" not in self.extensiontype_:
                imported_ns_type_prefix_ = GenerateDSNamespaceTypePrefixes_.get(self.extensiontype_, '')
                outfile.write(' xsi:type="%s%s"' % (imported_ns_type_prefix_, self.extensiontype_))
            else:
                outfile.write(' xsi:type="%s"' % self.extensiontype_)
    def _exportChildren(self, outfile, level, namespaceprefix_='', namespacedef_='', name_='programmer', fromsubclass_=False, pretty_print=True):
        super(programmer, self)._exportChildren(outfile, level, namespaceprefix_, namespacedef_, name_, True, pretty_print=pretty_print)
        if pretty_print:
            eol_ = '\n'
        else:
            eol_ = ''
        if self.email is not None:
            namespaceprefix_ = self.email_nsprefix_ + ':' if (UseCapturedNS_ and self.email_nsprefix_) else ''
            showIndent(outfile, level, pretty_print)
            outfile.write('<%semail>%s</%semail>%s' % (namespaceprefix_ , self.gds_encode(self.gds_format_string(quote_xml(self.email), input_name='email')), namespaceprefix_ , eol_))
        if self.elposint is not None:
            namespaceprefix_ = self.elposint_nsprefix_ + ':' if (UseCapturedNS_ and self.elposint_nsprefix_) else ''
            showIndent(outfile, level, pretty_print)
            outfile.write('<%selposint>%s</%selposint>%s' % (namespaceprefix_ , self.gds_format_integer(self.elposint, input_name='elposint'), namespaceprefix_ , eol_))
        if self.elnonposint is not None:
            namespaceprefix_ = self.elnonposint_nsprefix_ + ':' if (UseCapturedNS_ and self.elnonposint_nsprefix_) else ''
            showIndent(outfile, level, pretty_print)
            outfile.write('<%selnonposint>%s</%selnonposint>%s' % (namespaceprefix_ , self.gds_format_integer(self.elnonposint, input_name='elnonposint'), namespaceprefix_ , eol_))
        if self.elnegint is not None:
            namespaceprefix_ = self.elnegint_nsprefix_ + ':' if (UseCapturedNS_ and self.elnegint_nsprefix_) else ''
            showIndent(outfile, level, pretty_print)
            outfile.write('<%selnegint>%s</%selnegint>%s' % (namespaceprefix_ , self.gds_format_integer(self.elnegint, input_name='elnegint'), namespaceprefix_ , eol_))
        if self.elnonnegint is not None:
            namespaceprefix_ = self.elnonnegint_nsprefix_ + ':' if (UseCapturedNS_ and self.elnonnegint_nsprefix_) else ''
            showIndent(outfile, level, pretty_print)
            outfile.write('<%selnonnegint>%s</%selnonnegint>%s' % (namespaceprefix_ , self.gds_format_integer(self.elnonnegint, input_name='elnonnegint'), namespaceprefix_ , eol_))
        if self.eldate is not None:
            namespaceprefix_ = self.eldate_nsprefix_ + ':' if (UseCapturedNS_ and self.eldate_nsprefix_) else ''
            showIndent(outfile, level, pretty_print)
            outfile.write('<%seldate>%s</%seldate>%s' % (namespaceprefix_ , self.gds_format_date(self.eldate, input_name='eldate'), namespaceprefix_ , eol_))
        if self.eldatetime is not None:
            namespaceprefix_ = self.eldatetime_nsprefix_ + ':' if (UseCapturedNS_ and self.eldatetime_nsprefix_) else ''
            showIndent(outfile, level, pretty_print)
            outfile.write('<%seldatetime>%s</%seldatetime>%s' % (namespaceprefix_ , self.gds_format_datetime(self.eldatetime, input_name='eldatetime'), namespaceprefix_ , eol_))
        if self.eltoken is not None:
            namespaceprefix_ = self.eltoken_nsprefix_ + ':' if (UseCapturedNS_ and self.eltoken_nsprefix_) else ''
            showIndent(outfile, level, pretty_print)
            outfile.write('<%seltoken>%s</%seltoken>%s' % (namespaceprefix_ , self.gds_encode(self.gds_format_string(quote_xml(self.eltoken), input_name='eltoken')), namespaceprefix_ , eol_))
        if self.elshort is not None:
            namespaceprefix_ = self.elshort_nsprefix_ + ':' if (UseCapturedNS_ and self.elshort_nsprefix_) else ''
            showIndent(outfile, level, pretty_print)
            outfile.write('<%selshort>%s</%selshort>%s' % (namespaceprefix_ , self.gds_format_integer(self.elshort, input_name='elshort'), namespaceprefix_ , eol_))
        if self.ellong is not None:
            namespaceprefix_ = self.ellong_nsprefix_ + ':' if (UseCapturedNS_ and self.ellong_nsprefix_) else ''
            showIndent(outfile, level, pretty_print)
            outfile.write('<%sellong>%s</%sellong>%s' % (namespaceprefix_ , self.gds_format_integer(self.ellong, input_name='ellong'), namespaceprefix_ , eol_))
        if self.elparam is not None:
            namespaceprefix_ = self.elparam_nsprefix_ + ':' if (UseCapturedNS_ and self.elparam_nsprefix_) else ''
            self.elparam.export(outfile, level, namespaceprefix_, namespacedef_='', name_='elparam', pretty_print=pretty_print)
        if self.elarraytypes is not None:
            namespaceprefix_ = self.elarraytypes_nsprefix_ + ':' if (UseCapturedNS_ and self.elarraytypes_nsprefix_) else ''
            showIndent(outfile, level, pretty_print)
            outfile.write('<%selarraytypes>%s</%selarraytypes>%s' % (namespaceprefix_ , self.gds_encode(self.gds_format_string(quote_xml(self.elarraytypes), input_name='elarraytypes')), namespaceprefix_ , eol_))
    def exportLiteral(self, outfile, level, name_='programmer'):
        level += 1
        already_processed = set()
        self._exportLiteralAttributes(outfile, level, already_processed, name_)
        if self._hasContent():
            self._exportLiteralChildren(outfile, level, name_)
    def _exportLiteralAttributes(self, outfile, level, already_processed, name_):
        if self.language is not None and 'language' not in already_processed:
            already_processed.add('language')
            showIndent(outfile, level)
            outfile.write('language="%s",\n' % (self.language,))
        if self.area is not None and 'area' not in already_processed:
            already_processed.add('area')
            showIndent(outfile, level)
            outfile.write('area="%s",\n' % (self.area,))
        if self.attrposint is not None and 'attrposint' not in already_processed:
            already_processed.add('attrposint')
            showIndent(outfile, level)
            outfile.write('attrposint=%d,\n' % (self.attrposint,))
        if self.attrnonposint is not None and 'attrnonposint' not in already_processed:
            already_processed.add('attrnonposint')
            showIndent(outfile, level)
            outfile.write('attrnonposint=%d,\n' % (self.attrnonposint,))
        if self.attrnegint is not None and 'attrnegint' not in already_processed:
            already_processed.add('attrnegint')
            showIndent(outfile, level)
            outfile.write('attrnegint=%d,\n' % (self.attrnegint,))
        if self.attrnonnegint is not None and 'attrnonnegint' not in already_processed:
            already_processed.add('attrnonnegint')
            showIndent(outfile, level)
            outfile.write('attrnonnegint=%d,\n' % (self.attrnonnegint,))
        super(programmer, self)._exportLiteralAttributes(outfile, level, already_processed, name_)
    def _exportLiteralChildren(self, outfile, level, name_):
        super(programmer, self)._exportLiteralChildren(outfile, level, name_)
        if self.email is not None:
            showIndent(outfile, level)
            outfile.write('email=%s,\n' % self.gds_encode(quote_python(self.email)))
        if self.elposint is not None:
            showIndent(outfile, level)
            outfile.write('elposint=%d,\n' % self.elposint)
        if self.elnonposint is not None:
            showIndent(outfile, level)
            outfile.write('elnonposint=%d,\n' % self.elnonposint)
        if self.elnegint is not None:
            showIndent(outfile, level)
            outfile.write('elnegint=%d,\n' % self.elnegint)
        if self.elnonnegint is not None:
            showIndent(outfile, level)
            outfile.write('elnonnegint=%d,\n' % self.elnonnegint)
        if self.eldate is not None:
            showIndent(outfile, level)
            outfile.write('eldate=model_.GeneratedsSuper.gds_parse_date("%s"),\n' % self.gds_format_date(self.eldate, input_name='eldate'))
        if self.eldatetime is not None:
            showIndent(outfile, level)
            outfile.write('eldatetime=model_.GeneratedsSuper.gds_parse_datetime("%s"),\n' % self.gds_format_datetime(self.eldatetime, input_name='eldatetime'))
        if self.eltoken is not None:
            showIndent(outfile, level)
            outfile.write('eltoken=%s,\n' % self.gds_encode(quote_python(self.eltoken)))
        if self.elshort is not None:
            showIndent(outfile, level)
            outfile.write('elshort=%d,\n' % self.elshort)
        if self.ellong is not None:
            showIndent(outfile, level)
            outfile.write('ellong=%d,\n' % self.ellong)
        if self.elparam is not None:
            showIndent(outfile, level)
            outfile.write('elparam=model_.param(\n')
            self.elparam.exportLiteral(outfile, level, name_='elparam')
            showIndent(outfile, level)
            outfile.write('),\n')
        if self.elarraytypes is not None:
            showIndent(outfile, level)
            outfile.write('elarraytypes=%s,\n' % self.gds_encode(quote_python(self.elarraytypes)))
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
        super(programmer, self)._buildAttributes(node, attrs, already_processed)
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
            obj_ = param.factory(parent_object_=self)
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
        super(programmer, self)._buildChildren(child_, node, nodeName_, True)
    def walk_and_update(self):
        members = programmer._member_data_items
        for member in members:
            obj1 = getattr(self, member.get_name())
            if member.get_data_type() == 'xs:date':
                newvalue = date_calcs.date_from_string(obj1)
                setattr(self, member.get_name(), newvalue)
            elif member.get_container():
                for child in obj1:
                    if type(child) == types.InstanceType:
                        child.walk_and_update()
            else:
                obj1 = getattr(self, member.get_name())
                if type(obj1) == types.InstanceType:
                    obj1.walk_and_update()
        if programmer.superclass != None:
          programmer.superclass.walk_and_update(self)
    def walk_and_show(self, depth):
        global counter
        counter += 1
        depth += 1
        print('%d. class: programmer  depth: %d' % (counter, depth, ))
        members = programmer._member_data_items
        for member in members:
            s1 = member.get_name()
            s2 = member.get_data_type()
            s3 = '%d' % member.get_container()
            obj1 = getattr(self, member.get_name())
            if member.get_container():
                s4 = '<container>'
            else:
                if type(obj1) != types.InstanceType:
                    s4 = '%s' % obj1
                else:
                    s4 = '<instance>'
            s5 = '%s%s%s  %s' % (s1.ljust(16), s2.ljust(16), s3.rjust(4), s4, )
            print('   ', s5)
        for member in members:
            if member.get_container():
                for child in getattr(self, member.get_name()):
                    if type(child) == types.InstanceType:
                        child.walk_and_show(depth)
            else:
                obj1 = getattr(self, member.get_name())
                if type(obj1) == types.InstanceType:
                    obj1.walk_and_show(depth)
# end class programmer


class param(GeneratedsSuper):
    """param -- Finding flow attribute unneccesary in practice. A unnamed parameter is unbound/skipped.
    
    """
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
        self.flow = _cast(None, flow)
        self.flow_nsprefix_ = None
        self.semantic = _cast(None, semantic)
        self.semantic_nsprefix_ = None
        self.type_ = _cast(None, type_)
        self.type__nsprefix_ = None
        self.valueOf_ = valueOf_
    def factory(*args_, **kwargs_):
        if CurrentSubclassModule_ is not None:
            subclass = getSubclassFromModule_(
                CurrentSubclassModule_, param)
            if subclass is not None:
                return subclass(*args_, **kwargs_)
        if param.subclass:
            return param.subclass(*args_, **kwargs_)
        else:
            return param(*args_, **kwargs_)
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
    def _hasContent(self):
        if (
            (1 if type(self.valueOf_) in [int,float] else self.valueOf_)
        ):
            return True
        else:
            return False
    def export(self, outfile, level, namespaceprefix_='', namespacedef_='', name_='param', pretty_print=True):
        imported_ns_def_ = GenerateDSNamespaceDefs_.get('param')
        if imported_ns_def_ is not None:
            namespacedef_ = imported_ns_def_
        if pretty_print:
            eol_ = '\n'
        else:
            eol_ = ''
        if self.original_tagname_ is not None and name_ == 'param':
            name_ = self.original_tagname_
        if UseCapturedNS_ and self.ns_prefix_:
            namespaceprefix_ = self.ns_prefix_ + ':'
        showIndent(outfile, level, pretty_print)
        outfile.write('<%s%s%s' % (namespaceprefix_, name_, namespacedef_ and ' ' + namespacedef_ or '', ))
        already_processed = set()
        self._exportAttributes(outfile, level, already_processed, namespaceprefix_, name_='param')
        if self._hasContent():
            outfile.write('>')
            outfile.write(self.convert_unicode(self.valueOf_))
            self._exportChildren(outfile, level + 1, namespaceprefix_, namespacedef_, name_='param', pretty_print=pretty_print)
            outfile.write('</%s%s>%s' % (namespaceprefix_, name_, eol_))
        else:
            outfile.write('/>%s' % (eol_, ))
    def _exportAttributes(self, outfile, level, already_processed, namespaceprefix_='', name_='param'):
        if self.id is not None and 'id' not in already_processed:
            already_processed.add('id')
            outfile.write(' id=%s' % (self.gds_encode(self.gds_format_string(quote_attrib(self.id), input_name='id')), ))
        if self.name is not None and 'name' not in already_processed:
            already_processed.add('name')
            outfile.write(' name=%s' % (self.gds_encode(self.gds_format_string(quote_attrib(self.name), input_name='name')), ))
        if self.sid is not None and 'sid' not in already_processed:
            already_processed.add('sid')
            outfile.write(' sid=%s' % (self.gds_encode(self.gds_format_string(quote_attrib(self.sid), input_name='sid')), ))
        if self.flow is not None and 'flow' not in already_processed:
            already_processed.add('flow')
            outfile.write(' flow=%s' % (quote_attrib(self.flow), ))
        if self.semantic is not None and 'semantic' not in already_processed:
            already_processed.add('semantic')
            outfile.write(' semantic=%s' % (self.gds_encode(self.gds_format_string(quote_attrib(self.semantic), input_name='semantic')), ))
        if self.type_ is not None and 'type_' not in already_processed:
            already_processed.add('type_')
            outfile.write(' type=%s' % (self.gds_encode(self.gds_format_string(quote_attrib(self.type_), input_name='type')), ))
    def _exportChildren(self, outfile, level, namespaceprefix_='', namespacedef_='', name_='param', fromsubclass_=False, pretty_print=True):
        pass
    def exportLiteral(self, outfile, level, name_='param'):
        level += 1
        already_processed = set()
        self._exportLiteralAttributes(outfile, level, already_processed, name_)
        if self._hasContent():
            self._exportLiteralChildren(outfile, level, name_)
        showIndent(outfile, level)
        outfile.write('valueOf_ = """%s""",\n' % (self.valueOf_,))
    def _exportLiteralAttributes(self, outfile, level, already_processed, name_):
        if self.id is not None and 'id' not in already_processed:
            already_processed.add('id')
            showIndent(outfile, level)
            outfile.write('id="%s",\n' % (self.id,))
        if self.name is not None and 'name' not in already_processed:
            already_processed.add('name')
            showIndent(outfile, level)
            outfile.write('name="%s",\n' % (self.name,))
        if self.sid is not None and 'sid' not in already_processed:
            already_processed.add('sid')
            showIndent(outfile, level)
            outfile.write('sid="%s",\n' % (self.sid,))
        if self.flow is not None and 'flow' not in already_processed:
            already_processed.add('flow')
            showIndent(outfile, level)
            outfile.write('flow=%s,\n' % (self.flow,))
        if self.semantic is not None and 'semantic' not in already_processed:
            already_processed.add('semantic')
            showIndent(outfile, level)
            outfile.write('semantic="%s",\n' % (self.semantic,))
        if self.type_ is not None and 'type_' not in already_processed:
            already_processed.add('type_')
            showIndent(outfile, level)
            outfile.write('type_="%s",\n' % (self.type_,))
    def _exportLiteralChildren(self, outfile, level, name_):
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
            self.flow = value
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
    def walk_and_update(self):
        members = param._member_data_items
        for member in members:
            obj1 = getattr(self, member.get_name())
            if member.get_data_type() == 'xs:date':
                newvalue = date_calcs.date_from_string(obj1)
                setattr(self, member.get_name(), newvalue)
            elif member.get_container():
                for child in obj1:
                    if type(child) == types.InstanceType:
                        child.walk_and_update()
            else:
                obj1 = getattr(self, member.get_name())
                if type(obj1) == types.InstanceType:
                    obj1.walk_and_update()
        if param.superclass != None:
          param.superclass.walk_and_update(self)
    def walk_and_show(self, depth):
        global counter
        counter += 1
        depth += 1
        print('%d. class: param  depth: %d' % (counter, depth, ))
        members = param._member_data_items
        for member in members:
            s1 = member.get_name()
            s2 = member.get_data_type()
            s3 = '%d' % member.get_container()
            obj1 = getattr(self, member.get_name())
            if member.get_container():
                s4 = '<container>'
            else:
                if type(obj1) != types.InstanceType:
                    s4 = '%s' % obj1
                else:
                    s4 = '<instance>'
            s5 = '%s%s%s  %s' % (s1.ljust(16), s2.ljust(16), s3.rjust(4), s4, )
            print('   ', s5)
        for member in members:
            if member.get_container():
                for child in getattr(self, member.get_name()):
                    if type(child) == types.InstanceType:
                        child.walk_and_show(depth)
            else:
                obj1 = getattr(self, member.get_name())
                if type(obj1) == types.InstanceType:
                    obj1.walk_and_show(depth)
# end class param


class python_programmer(programmer):
    __hash__ = GeneratedsSuper.__hash__
    member_data_items_ = [
        MemberSpec_('nick_name', 'xs:string', 0, 1, {'use': 'optional', 'name': 'nick-name'}),
        MemberSpec_('favorite_editor', 'xs:string', 0, 0, {'name': 'favorite-editor', 'type': 'xs:string'}, None),
    ]
    subclass = None
    superclass = programmer
    def __init__(self, value=None, id=None, ratio=None, fruit=None, vegetable=None, name=None, interest=None, category=None, agent=None, promoter=None, description=None, language=None, area=None, attrposint=None, attrnonposint=None, attrnegint=None, attrnonnegint=None, email=None, elposint=None, elnonposint=None, elnegint=None, elnonnegint=None, eldate=None, eldatetime=None, eltoken=None, elshort=None, ellong=None, elparam=None, elarraytypes=None, nick_name=None, favorite_editor=None, gds_collector_=None, **kwargs_):
        self.gds_collector_ = gds_collector_
        self.gds_elementtree_node_ = None
        self.original_tagname_ = None
        self.parent_object_ = kwargs_.get('parent_object_')
        self.ns_prefix_ = None
        super(globals().get("python_programmer"), self).__init__(value, id, ratio, fruit, vegetable, name, interest, category, agent, promoter, description, language, area, attrposint, attrnonposint, attrnegint, attrnonnegint, email, elposint, elnonposint, elnegint, elnonnegint, eldate, eldatetime, eltoken, elshort, ellong, elparam, elarraytypes,  **kwargs_)
        self.nick_name = _cast(None, nick_name)
        self.nick_name_nsprefix_ = None
        self.favorite_editor = favorite_editor
        self.favorite_editor_nsprefix_ = None
    def factory(*args_, **kwargs_):
        if CurrentSubclassModule_ is not None:
            subclass = getSubclassFromModule_(
                CurrentSubclassModule_, python_programmer)
            if subclass is not None:
                return subclass(*args_, **kwargs_)
        if python_programmer.subclass:
            return python_programmer.subclass(*args_, **kwargs_)
        else:
            return python_programmer(*args_, **kwargs_)
    factory = staticmethod(factory)
    def get_ns_prefix_(self):
        return self.ns_prefix_
    def set_ns_prefix_(self, ns_prefix):
        self.ns_prefix_ = ns_prefix
    def get_favorite_editor(self):
        return self.favorite_editor
    def set_favorite_editor(self, favorite_editor):
        self.favorite_editor = favorite_editor
    def get_nick_name(self):
        return self.nick_name
    def set_nick_name(self, nick_name):
        self.nick_name = nick_name
    def _hasContent(self):
        if (
            self.favorite_editor is not None or
            super(python_programmer, self)._hasContent()
        ):
            return True
        else:
            return False
    def export(self, outfile, level, namespaceprefix_='', namespacedef_='', name_='python-programmer', pretty_print=True):
        imported_ns_def_ = GenerateDSNamespaceDefs_.get('python-programmer')
        if imported_ns_def_ is not None:
            namespacedef_ = imported_ns_def_
        if pretty_print:
            eol_ = '\n'
        else:
            eol_ = ''
        if self.original_tagname_ is not None and name_ == 'python-programmer':
            name_ = self.original_tagname_
        if UseCapturedNS_ and self.ns_prefix_:
            namespaceprefix_ = self.ns_prefix_ + ':'
        showIndent(outfile, level, pretty_print)
        outfile.write('<%s%s%s' % (namespaceprefix_, name_, namespacedef_ and ' ' + namespacedef_ or '', ))
        already_processed = set()
        self._exportAttributes(outfile, level, already_processed, namespaceprefix_, name_='python-programmer')
        if self._hasContent():
            outfile.write('>%s' % (eol_, ))
            self._exportChildren(outfile, level + 1, namespaceprefix_, namespacedef_, name_='python-programmer', pretty_print=pretty_print)
            showIndent(outfile, level, pretty_print)
            outfile.write('</%s%s>%s' % (namespaceprefix_, name_, eol_))
        else:
            outfile.write('/>%s' % (eol_, ))
    def _exportAttributes(self, outfile, level, already_processed, namespaceprefix_='', name_='python-programmer'):
        super(python_programmer, self)._exportAttributes(outfile, level, already_processed, namespaceprefix_, name_='python-programmer')
        if self.nick_name is not None and 'nick_name' not in already_processed:
            already_processed.add('nick_name')
            outfile.write(' nick-name=%s' % (self.gds_encode(self.gds_format_string(quote_attrib(self.nick_name), input_name='nick-name')), ))
    def _exportChildren(self, outfile, level, namespaceprefix_='', namespacedef_='', name_='python-programmer', fromsubclass_=False, pretty_print=True):
        super(python_programmer, self)._exportChildren(outfile, level, namespaceprefix_, namespacedef_, name_, True, pretty_print=pretty_print)
        if pretty_print:
            eol_ = '\n'
        else:
            eol_ = ''
        if self.favorite_editor is not None:
            namespaceprefix_ = self.favorite_editor_nsprefix_ + ':' if (UseCapturedNS_ and self.favorite_editor_nsprefix_) else ''
            showIndent(outfile, level, pretty_print)
            outfile.write('<%sfavorite-editor>%s</%sfavorite-editor>%s' % (namespaceprefix_ , self.gds_encode(self.gds_format_string(quote_xml(self.favorite_editor), input_name='favorite-editor')), namespaceprefix_ , eol_))
    def exportLiteral(self, outfile, level, name_='python-programmer'):
        level += 1
        already_processed = set()
        self._exportLiteralAttributes(outfile, level, already_processed, name_)
        if self._hasContent():
            self._exportLiteralChildren(outfile, level, name_)
    def _exportLiteralAttributes(self, outfile, level, already_processed, name_):
        if self.nick_name is not None and 'nick_name' not in already_processed:
            already_processed.add('nick_name')
            showIndent(outfile, level)
            outfile.write('nick_name="%s",\n' % (self.nick_name,))
        super(python_programmer, self)._exportLiteralAttributes(outfile, level, already_processed, name_)
    def _exportLiteralChildren(self, outfile, level, name_):
        super(python_programmer, self)._exportLiteralChildren(outfile, level, name_)
        if self.favorite_editor is not None:
            showIndent(outfile, level)
            outfile.write('favorite_editor=%s,\n' % self.gds_encode(quote_python(self.favorite_editor)))
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
        super(python_programmer, self)._buildAttributes(node, attrs, already_processed)
    def _buildChildren(self, child_, node, nodeName_, fromsubclass_=False, gds_collector_=None):
        if nodeName_ == 'favorite-editor':
            value_ = child_.text
            value_ = self.gds_parse_string(value_, node, 'favorite_editor')
            value_ = self.gds_validate_string(value_, node, 'favorite_editor')
            self.favorite_editor = value_
            self.favorite_editor_nsprefix_ = child_.prefix
        super(python_programmer, self)._buildChildren(child_, node, nodeName_, True)
    def walk_and_update(self):
        members = python_programmer._member_data_items
        for member in members:
            obj1 = getattr(self, member.get_name())
            if member.get_data_type() == 'xs:date':
                newvalue = date_calcs.date_from_string(obj1)
                setattr(self, member.get_name(), newvalue)
            elif member.get_container():
                for child in obj1:
                    if type(child) == types.InstanceType:
                        child.walk_and_update()
            else:
                obj1 = getattr(self, member.get_name())
                if type(obj1) == types.InstanceType:
                    obj1.walk_and_update()
        if python_programmer.superclass != None:
          python_programmer.superclass.walk_and_update(self)
    def walk_and_show(self, depth):
        global counter
        counter += 1
        depth += 1
        print('%d. class: python_programmer  depth: %d' % (counter, depth, ))
        members = python_programmer._member_data_items
        for member in members:
            s1 = member.get_name()
            s2 = member.get_data_type()
            s3 = '%d' % member.get_container()
            obj1 = getattr(self, member.get_name())
            if member.get_container():
                s4 = '<container>'
            else:
                if type(obj1) != types.InstanceType:
                    s4 = '%s' % obj1
                else:
                    s4 = '<instance>'
            s5 = '%s%s%s  %s' % (s1.ljust(16), s2.ljust(16), s3.rjust(4), s4, )
            print('   ', s5)
        for member in members:
            if member.get_container():
                for child in getattr(self, member.get_name()):
                    if type(child) == types.InstanceType:
                        child.walk_and_show(depth)
            else:
                obj1 = getattr(self, member.get_name())
                if type(obj1) == types.InstanceType:
                    obj1.walk_and_show(depth)
# end class python_programmer


class java_programmer(programmer):
    __hash__ = GeneratedsSuper.__hash__
    member_data_items_ = [
        MemberSpec_('nick_name', 'xs:string', 0, 1, {'use': 'optional', 'name': 'nick-name'}),
        MemberSpec_('status', 'xs:string', 0, 1, {'use': 'optional', 'name': 'status'}),
        MemberSpec_('favorite_editor', 'xs:string', 0, 0, {'name': 'favorite-editor', 'type': 'xs:string'}, None),
    ]
    subclass = None
    superclass = programmer
    def __init__(self, value=None, id=None, ratio=None, fruit=None, vegetable=None, name=None, interest=None, category=None, agent=None, promoter=None, description=None, language=None, area=None, attrposint=None, attrnonposint=None, attrnegint=None, attrnonnegint=None, email=None, elposint=None, elnonposint=None, elnegint=None, elnonnegint=None, eldate=None, eldatetime=None, eltoken=None, elshort=None, ellong=None, elparam=None, elarraytypes=None, nick_name=None, status=None, favorite_editor=None, gds_collector_=None, **kwargs_):
        self.gds_collector_ = gds_collector_
        self.gds_elementtree_node_ = None
        self.original_tagname_ = None
        self.parent_object_ = kwargs_.get('parent_object_')
        self.ns_prefix_ = None
        super(globals().get("java_programmer"), self).__init__(value, id, ratio, fruit, vegetable, name, interest, category, agent, promoter, description, language, area, attrposint, attrnonposint, attrnegint, attrnonnegint, email, elposint, elnonposint, elnegint, elnonnegint, eldate, eldatetime, eltoken, elshort, ellong, elparam, elarraytypes,  **kwargs_)
        self.nick_name = _cast(None, nick_name)
        self.nick_name_nsprefix_ = None
        self.status = _cast(None, status)
        self.status_nsprefix_ = None
        self.favorite_editor = favorite_editor
        self.favorite_editor_nsprefix_ = None
    def factory(*args_, **kwargs_):
        if CurrentSubclassModule_ is not None:
            subclass = getSubclassFromModule_(
                CurrentSubclassModule_, java_programmer)
            if subclass is not None:
                return subclass(*args_, **kwargs_)
        if java_programmer.subclass:
            return java_programmer.subclass(*args_, **kwargs_)
        else:
            return java_programmer(*args_, **kwargs_)
    factory = staticmethod(factory)
    def get_ns_prefix_(self):
        return self.ns_prefix_
    def set_ns_prefix_(self, ns_prefix):
        self.ns_prefix_ = ns_prefix
    def get_favorite_editor(self):
        return self.favorite_editor
    def set_favorite_editor(self, favorite_editor):
        self.favorite_editor = favorite_editor
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
            super(java_programmer, self)._hasContent()
        ):
            return True
        else:
            return False
    def export(self, outfile, level, namespaceprefix_='', namespacedef_='', name_='java-programmer', pretty_print=True):
        imported_ns_def_ = GenerateDSNamespaceDefs_.get('java-programmer')
        if imported_ns_def_ is not None:
            namespacedef_ = imported_ns_def_
        if pretty_print:
            eol_ = '\n'
        else:
            eol_ = ''
        if self.original_tagname_ is not None and name_ == 'java-programmer':
            name_ = self.original_tagname_
        if UseCapturedNS_ and self.ns_prefix_:
            namespaceprefix_ = self.ns_prefix_ + ':'
        showIndent(outfile, level, pretty_print)
        outfile.write('<%s%s%s' % (namespaceprefix_, name_, namespacedef_ and ' ' + namespacedef_ or '', ))
        already_processed = set()
        self._exportAttributes(outfile, level, already_processed, namespaceprefix_, name_='java-programmer')
        if self._hasContent():
            outfile.write('>%s' % (eol_, ))
            self._exportChildren(outfile, level + 1, namespaceprefix_, namespacedef_, name_='java-programmer', pretty_print=pretty_print)
            showIndent(outfile, level, pretty_print)
            outfile.write('</%s%s>%s' % (namespaceprefix_, name_, eol_))
        else:
            outfile.write('/>%s' % (eol_, ))
    def _exportAttributes(self, outfile, level, already_processed, namespaceprefix_='', name_='java-programmer'):
        super(java_programmer, self)._exportAttributes(outfile, level, already_processed, namespaceprefix_, name_='java-programmer')
        if self.nick_name is not None and 'nick_name' not in already_processed:
            already_processed.add('nick_name')
            outfile.write(' nick-name=%s' % (self.gds_encode(self.gds_format_string(quote_attrib(self.nick_name), input_name='nick-name')), ))
        if self.status is not None and 'status' not in already_processed:
            already_processed.add('status')
            outfile.write(' status=%s' % (self.gds_encode(self.gds_format_string(quote_attrib(self.status), input_name='status')), ))
    def _exportChildren(self, outfile, level, namespaceprefix_='', namespacedef_='', name_='java-programmer', fromsubclass_=False, pretty_print=True):
        super(java_programmer, self)._exportChildren(outfile, level, namespaceprefix_, namespacedef_, name_, True, pretty_print=pretty_print)
        if pretty_print:
            eol_ = '\n'
        else:
            eol_ = ''
        if self.favorite_editor is not None:
            namespaceprefix_ = self.favorite_editor_nsprefix_ + ':' if (UseCapturedNS_ and self.favorite_editor_nsprefix_) else ''
            showIndent(outfile, level, pretty_print)
            outfile.write('<%sfavorite-editor>%s</%sfavorite-editor>%s' % (namespaceprefix_ , self.gds_encode(self.gds_format_string(quote_xml(self.favorite_editor), input_name='favorite-editor')), namespaceprefix_ , eol_))
    def exportLiteral(self, outfile, level, name_='java-programmer'):
        level += 1
        already_processed = set()
        self._exportLiteralAttributes(outfile, level, already_processed, name_)
        if self._hasContent():
            self._exportLiteralChildren(outfile, level, name_)
    def _exportLiteralAttributes(self, outfile, level, already_processed, name_):
        if self.nick_name is not None and 'nick_name' not in already_processed:
            already_processed.add('nick_name')
            showIndent(outfile, level)
            outfile.write('nick_name="%s",\n' % (self.nick_name,))
        if self.status is not None and 'status' not in already_processed:
            already_processed.add('status')
            showIndent(outfile, level)
            outfile.write('status="%s",\n' % (self.status,))
        super(java_programmer, self)._exportLiteralAttributes(outfile, level, already_processed, name_)
    def _exportLiteralChildren(self, outfile, level, name_):
        super(java_programmer, self)._exportLiteralChildren(outfile, level, name_)
        if self.favorite_editor is not None:
            showIndent(outfile, level)
            outfile.write('favorite_editor=%s,\n' % self.gds_encode(quote_python(self.favorite_editor)))
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
        super(java_programmer, self)._buildAttributes(node, attrs, already_processed)
    def _buildChildren(self, child_, node, nodeName_, fromsubclass_=False, gds_collector_=None):
        if nodeName_ == 'favorite-editor':
            value_ = child_.text
            value_ = self.gds_parse_string(value_, node, 'favorite_editor')
            value_ = self.gds_validate_string(value_, node, 'favorite_editor')
            self.favorite_editor = value_
            self.favorite_editor_nsprefix_ = child_.prefix
        super(java_programmer, self)._buildChildren(child_, node, nodeName_, True)
    def walk_and_update(self):
        members = java_programmer._member_data_items
        for member in members:
            obj1 = getattr(self, member.get_name())
            if member.get_data_type() == 'xs:date':
                newvalue = date_calcs.date_from_string(obj1)
                setattr(self, member.get_name(), newvalue)
            elif member.get_container():
                for child in obj1:
                    if type(child) == types.InstanceType:
                        child.walk_and_update()
            else:
                obj1 = getattr(self, member.get_name())
                if type(obj1) == types.InstanceType:
                    obj1.walk_and_update()
        if java_programmer.superclass != None:
          java_programmer.superclass.walk_and_update(self)
    def walk_and_show(self, depth):
        global counter
        counter += 1
        depth += 1
        print('%d. class: java_programmer  depth: %d' % (counter, depth, ))
        members = java_programmer._member_data_items
        for member in members:
            s1 = member.get_name()
            s2 = member.get_data_type()
            s3 = '%d' % member.get_container()
            obj1 = getattr(self, member.get_name())
            if member.get_container():
                s4 = '<container>'
            else:
                if type(obj1) != types.InstanceType:
                    s4 = '%s' % obj1
                else:
                    s4 = '<instance>'
            s5 = '%s%s%s  %s' % (s1.ljust(16), s2.ljust(16), s3.rjust(4), s4, )
            print('   ', s5)
        for member in members:
            if member.get_container():
                for child in getattr(self, member.get_name()):
                    if type(child) == types.InstanceType:
                        child.walk_and_show(depth)
            else:
                obj1 = getattr(self, member.get_name())
                if type(obj1) == types.InstanceType:
                    obj1.walk_and_show(depth)
# end class java_programmer


class agent(GeneratedsSuper):
    __hash__ = GeneratedsSuper.__hash__
    member_data_items_ = [
        MemberSpec_('firstname', 'xs:string', 0, 0, {'name': 'firstname', 'type': 'xs:string'}, None),
        MemberSpec_('lastname', 'xs:string', 0, 0, {'name': 'lastname', 'type': 'xs:string'}, None),
        MemberSpec_('priority', 'xs:float', 0, 0, {'name': 'priority', 'type': 'xs:float'}, None),
        MemberSpec_('info', 'info', 0, 0, {'name': 'info', 'type': 'info'}, None),
    ]
    subclass = None
    superclass = None
    def __init__(self, firstname=None, lastname=None, priority=None, info=None, gds_collector_=None, **kwargs_):
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
    def factory(*args_, **kwargs_):
        if CurrentSubclassModule_ is not None:
            subclass = getSubclassFromModule_(
                CurrentSubclassModule_, agent)
            if subclass is not None:
                return subclass(*args_, **kwargs_)
        if agent.subclass:
            return agent.subclass(*args_, **kwargs_)
        else:
            return agent(*args_, **kwargs_)
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
            self.info is not None
        ):
            return True
        else:
            return False
    def export(self, outfile, level, namespaceprefix_='', namespacedef_='', name_='agent', pretty_print=True):
        imported_ns_def_ = GenerateDSNamespaceDefs_.get('agent')
        if imported_ns_def_ is not None:
            namespacedef_ = imported_ns_def_
        if pretty_print:
            eol_ = '\n'
        else:
            eol_ = ''
        if self.original_tagname_ is not None and name_ == 'agent':
            name_ = self.original_tagname_
        if UseCapturedNS_ and self.ns_prefix_:
            namespaceprefix_ = self.ns_prefix_ + ':'
        showIndent(outfile, level, pretty_print)
        outfile.write('<%s%s%s' % (namespaceprefix_, name_, namespacedef_ and ' ' + namespacedef_ or '', ))
        already_processed = set()
        self._exportAttributes(outfile, level, already_processed, namespaceprefix_, name_='agent')
        if self._hasContent():
            outfile.write('>%s' % (eol_, ))
            self._exportChildren(outfile, level + 1, namespaceprefix_, namespacedef_, name_='agent', pretty_print=pretty_print)
            showIndent(outfile, level, pretty_print)
            outfile.write('</%s%s>%s' % (namespaceprefix_, name_, eol_))
        else:
            outfile.write('/>%s' % (eol_, ))
    def _exportAttributes(self, outfile, level, already_processed, namespaceprefix_='', name_='agent'):
        pass
    def _exportChildren(self, outfile, level, namespaceprefix_='', namespacedef_='', name_='agent', fromsubclass_=False, pretty_print=True):
        if pretty_print:
            eol_ = '\n'
        else:
            eol_ = ''
        if self.firstname is not None:
            namespaceprefix_ = self.firstname_nsprefix_ + ':' if (UseCapturedNS_ and self.firstname_nsprefix_) else ''
            showIndent(outfile, level, pretty_print)
            outfile.write('<%sfirstname>%s</%sfirstname>%s' % (namespaceprefix_ , self.gds_encode(self.gds_format_string(quote_xml(self.firstname), input_name='firstname')), namespaceprefix_ , eol_))
        if self.lastname is not None:
            namespaceprefix_ = self.lastname_nsprefix_ + ':' if (UseCapturedNS_ and self.lastname_nsprefix_) else ''
            showIndent(outfile, level, pretty_print)
            outfile.write('<%slastname>%s</%slastname>%s' % (namespaceprefix_ , self.gds_encode(self.gds_format_string(quote_xml(self.lastname), input_name='lastname')), namespaceprefix_ , eol_))
        if self.priority is not None:
            namespaceprefix_ = self.priority_nsprefix_ + ':' if (UseCapturedNS_ and self.priority_nsprefix_) else ''
            showIndent(outfile, level, pretty_print)
            outfile.write('<%spriority>%s</%spriority>%s' % (namespaceprefix_ , self.gds_format_float(self.priority, input_name='priority'), namespaceprefix_ , eol_))
        if self.info is not None:
            namespaceprefix_ = self.info_nsprefix_ + ':' if (UseCapturedNS_ and self.info_nsprefix_) else ''
            self.info.export(outfile, level, namespaceprefix_, namespacedef_='', name_='info', pretty_print=pretty_print)
    def exportLiteral(self, outfile, level, name_='agent'):
        level += 1
        already_processed = set()
        self._exportLiteralAttributes(outfile, level, already_processed, name_)
        if self._hasContent():
            self._exportLiteralChildren(outfile, level, name_)
    def _exportLiteralAttributes(self, outfile, level, already_processed, name_):
        pass
    def _exportLiteralChildren(self, outfile, level, name_):
        if self.firstname is not None:
            showIndent(outfile, level)
            outfile.write('firstname=%s,\n' % self.gds_encode(quote_python(self.firstname)))
        if self.lastname is not None:
            showIndent(outfile, level)
            outfile.write('lastname=%s,\n' % self.gds_encode(quote_python(self.lastname)))
        if self.priority is not None:
            showIndent(outfile, level)
            outfile.write('priority=%f,\n' % self.priority)
        if self.info is not None:
            showIndent(outfile, level)
            outfile.write('info=model_.info(\n')
            self.info.exportLiteral(outfile, level)
            showIndent(outfile, level)
            outfile.write('),\n')
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
            obj_ = info.factory(parent_object_=self)
            obj_.build(child_, gds_collector_=gds_collector_)
            self.info = obj_
            obj_.original_tagname_ = 'info'
    def walk_and_update(self):
        members = agent._member_data_items
        for member in members:
            obj1 = getattr(self, member.get_name())
            if member.get_data_type() == 'xs:date':
                newvalue = date_calcs.date_from_string(obj1)
                setattr(self, member.get_name(), newvalue)
            elif member.get_container():
                for child in obj1:
                    if type(child) == types.InstanceType:
                        child.walk_and_update()
            else:
                obj1 = getattr(self, member.get_name())
                if type(obj1) == types.InstanceType:
                    obj1.walk_and_update()
        if agent.superclass != None:
          agent.superclass.walk_and_update(self)
    def walk_and_show(self, depth):
        global counter
        counter += 1
        depth += 1
        print('%d. class: agent  depth: %d' % (counter, depth, ))
        members = agent._member_data_items
        for member in members:
            s1 = member.get_name()
            s2 = member.get_data_type()
            s3 = '%d' % member.get_container()
            obj1 = getattr(self, member.get_name())
            if member.get_container():
                s4 = '<container>'
            else:
                if type(obj1) != types.InstanceType:
                    s4 = '%s' % obj1
                else:
                    s4 = '<instance>'
            s5 = '%s%s%s  %s' % (s1.ljust(16), s2.ljust(16), s3.rjust(4), s4, )
            print('   ', s5)
        for member in members:
            if member.get_container():
                for child in getattr(self, member.get_name()):
                    if type(child) == types.InstanceType:
                        child.walk_and_show(depth)
            else:
                obj1 = getattr(self, member.get_name())
                if type(obj1) == types.InstanceType:
                    obj1.walk_and_show(depth)
# end class agent


class special_agent(GeneratedsSuper):
    __hash__ = GeneratedsSuper.__hash__
    member_data_items_ = [
        MemberSpec_('firstname', 'xs:string', 0, 0, {'name': 'firstname', 'type': 'xs:string'}, None),
        MemberSpec_('lastname', 'xs:string', 0, 0, {'name': 'lastname', 'type': 'xs:string'}, None),
        MemberSpec_('priority', 'xs:float', 0, 0, {'name': 'priority', 'type': 'xs:float'}, None),
        MemberSpec_('info', 'info', 0, 0, {'name': 'info', 'type': 'info'}, None),
    ]
    subclass = None
    superclass = None
    def __init__(self, firstname=None, lastname=None, priority=None, info=None, gds_collector_=None, **kwargs_):
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
    def factory(*args_, **kwargs_):
        if CurrentSubclassModule_ is not None:
            subclass = getSubclassFromModule_(
                CurrentSubclassModule_, special_agent)
            if subclass is not None:
                return subclass(*args_, **kwargs_)
        if special_agent.subclass:
            return special_agent.subclass(*args_, **kwargs_)
        else:
            return special_agent(*args_, **kwargs_)
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
            self.info is not None
        ):
            return True
        else:
            return False
    def export(self, outfile, level, namespaceprefix_='', namespacedef_='', name_='special-agent', pretty_print=True):
        imported_ns_def_ = GenerateDSNamespaceDefs_.get('special-agent')
        if imported_ns_def_ is not None:
            namespacedef_ = imported_ns_def_
        if pretty_print:
            eol_ = '\n'
        else:
            eol_ = ''
        if self.original_tagname_ is not None and name_ == 'special-agent':
            name_ = self.original_tagname_
        if UseCapturedNS_ and self.ns_prefix_:
            namespaceprefix_ = self.ns_prefix_ + ':'
        showIndent(outfile, level, pretty_print)
        outfile.write('<%s%s%s' % (namespaceprefix_, name_, namespacedef_ and ' ' + namespacedef_ or '', ))
        already_processed = set()
        self._exportAttributes(outfile, level, already_processed, namespaceprefix_, name_='special-agent')
        if self._hasContent():
            outfile.write('>%s' % (eol_, ))
            self._exportChildren(outfile, level + 1, namespaceprefix_, namespacedef_, name_='special-agent', pretty_print=pretty_print)
            showIndent(outfile, level, pretty_print)
            outfile.write('</%s%s>%s' % (namespaceprefix_, name_, eol_))
        else:
            outfile.write('/>%s' % (eol_, ))
    def _exportAttributes(self, outfile, level, already_processed, namespaceprefix_='', name_='special-agent'):
        pass
    def _exportChildren(self, outfile, level, namespaceprefix_='', namespacedef_='', name_='special-agent', fromsubclass_=False, pretty_print=True):
        if pretty_print:
            eol_ = '\n'
        else:
            eol_ = ''
        if self.firstname is not None:
            namespaceprefix_ = self.firstname_nsprefix_ + ':' if (UseCapturedNS_ and self.firstname_nsprefix_) else ''
            showIndent(outfile, level, pretty_print)
            outfile.write('<%sfirstname>%s</%sfirstname>%s' % (namespaceprefix_ , self.gds_encode(self.gds_format_string(quote_xml(self.firstname), input_name='firstname')), namespaceprefix_ , eol_))
        if self.lastname is not None:
            namespaceprefix_ = self.lastname_nsprefix_ + ':' if (UseCapturedNS_ and self.lastname_nsprefix_) else ''
            showIndent(outfile, level, pretty_print)
            outfile.write('<%slastname>%s</%slastname>%s' % (namespaceprefix_ , self.gds_encode(self.gds_format_string(quote_xml(self.lastname), input_name='lastname')), namespaceprefix_ , eol_))
        if self.priority is not None:
            namespaceprefix_ = self.priority_nsprefix_ + ':' if (UseCapturedNS_ and self.priority_nsprefix_) else ''
            showIndent(outfile, level, pretty_print)
            outfile.write('<%spriority>%s</%spriority>%s' % (namespaceprefix_ , self.gds_format_float(self.priority, input_name='priority'), namespaceprefix_ , eol_))
        if self.info is not None:
            namespaceprefix_ = self.info_nsprefix_ + ':' if (UseCapturedNS_ and self.info_nsprefix_) else ''
            self.info.export(outfile, level, namespaceprefix_, namespacedef_='', name_='info', pretty_print=pretty_print)
    def exportLiteral(self, outfile, level, name_='special-agent'):
        level += 1
        already_processed = set()
        self._exportLiteralAttributes(outfile, level, already_processed, name_)
        if self._hasContent():
            self._exportLiteralChildren(outfile, level, name_)
    def _exportLiteralAttributes(self, outfile, level, already_processed, name_):
        pass
    def _exportLiteralChildren(self, outfile, level, name_):
        if self.firstname is not None:
            showIndent(outfile, level)
            outfile.write('firstname=%s,\n' % self.gds_encode(quote_python(self.firstname)))
        if self.lastname is not None:
            showIndent(outfile, level)
            outfile.write('lastname=%s,\n' % self.gds_encode(quote_python(self.lastname)))
        if self.priority is not None:
            showIndent(outfile, level)
            outfile.write('priority=%f,\n' % self.priority)
        if self.info is not None:
            showIndent(outfile, level)
            outfile.write('info=model_.info(\n')
            self.info.exportLiteral(outfile, level)
            showIndent(outfile, level)
            outfile.write('),\n')
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
            obj_ = info.factory(parent_object_=self)
            obj_.build(child_, gds_collector_=gds_collector_)
            self.info = obj_
            obj_.original_tagname_ = 'info'
    def walk_and_update(self):
        members = special_agent._member_data_items
        for member in members:
            obj1 = getattr(self, member.get_name())
            if member.get_data_type() == 'xs:date':
                newvalue = date_calcs.date_from_string(obj1)
                setattr(self, member.get_name(), newvalue)
            elif member.get_container():
                for child in obj1:
                    if type(child) == types.InstanceType:
                        child.walk_and_update()
            else:
                obj1 = getattr(self, member.get_name())
                if type(obj1) == types.InstanceType:
                    obj1.walk_and_update()
        if special_agent.superclass != None:
          special_agent.superclass.walk_and_update(self)
    def walk_and_show(self, depth):
        global counter
        counter += 1
        depth += 1
        print('%d. class: special_agent  depth: %d' % (counter, depth, ))
        members = special_agent._member_data_items
        for member in members:
            s1 = member.get_name()
            s2 = member.get_data_type()
            s3 = '%d' % member.get_container()
            obj1 = getattr(self, member.get_name())
            if member.get_container():
                s4 = '<container>'
            else:
                if type(obj1) != types.InstanceType:
                    s4 = '%s' % obj1
                else:
                    s4 = '<instance>'
            s5 = '%s%s%s  %s' % (s1.ljust(16), s2.ljust(16), s3.rjust(4), s4, )
            print('   ', s5)
        for member in members:
            if member.get_container():
                for child in getattr(self, member.get_name()):
                    if type(child) == types.InstanceType:
                        child.walk_and_show(depth)
            else:
                obj1 = getattr(self, member.get_name())
                if type(obj1) == types.InstanceType:
                    obj1.walk_and_show(depth)
# end class special_agent


class booster(GeneratedsSuper):
    __hash__ = GeneratedsSuper.__hash__
    member_data_items_ = [
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
    def __init__(self, firstname=None, lastname=None, other_name=None, class_=None, other_value=None, type_=None, client_handler=None, gds_collector_=None, **kwargs_):
        self.gds_collector_ = gds_collector_
        self.gds_elementtree_node_ = None
        self.original_tagname_ = None
        self.parent_object_ = kwargs_.get('parent_object_')
        self.ns_prefix_ = None
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
                CurrentSubclassModule_, booster)
            if subclass is not None:
                return subclass(*args_, **kwargs_)
        if booster.subclass:
            return booster.subclass(*args_, **kwargs_)
        else:
            return booster(*args_, **kwargs_)
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
    def export(self, outfile, level, namespaceprefix_='', namespacedef_='', name_='booster', pretty_print=True):
        imported_ns_def_ = GenerateDSNamespaceDefs_.get('booster')
        if imported_ns_def_ is not None:
            namespacedef_ = imported_ns_def_
        if pretty_print:
            eol_ = '\n'
        else:
            eol_ = ''
        if self.original_tagname_ is not None and name_ == 'booster':
            name_ = self.original_tagname_
        if UseCapturedNS_ and self.ns_prefix_:
            namespaceprefix_ = self.ns_prefix_ + ':'
        showIndent(outfile, level, pretty_print)
        outfile.write('<%s%s%s' % (namespaceprefix_, name_, namespacedef_ and ' ' + namespacedef_ or '', ))
        already_processed = set()
        self._exportAttributes(outfile, level, already_processed, namespaceprefix_, name_='booster')
        if self._hasContent():
            outfile.write('>%s' % (eol_, ))
            self._exportChildren(outfile, level + 1, namespaceprefix_, namespacedef_, name_='booster', pretty_print=pretty_print)
            showIndent(outfile, level, pretty_print)
            outfile.write('</%s%s>%s' % (namespaceprefix_, name_, eol_))
        else:
            outfile.write('/>%s' % (eol_, ))
    def _exportAttributes(self, outfile, level, already_processed, namespaceprefix_='', name_='booster'):
        pass
    def _exportChildren(self, outfile, level, namespaceprefix_='', namespacedef_='', name_='booster', fromsubclass_=False, pretty_print=True):
        if pretty_print:
            eol_ = '\n'
        else:
            eol_ = ''
        if self.firstname is not None:
            namespaceprefix_ = self.firstname_nsprefix_ + ':' if (UseCapturedNS_ and self.firstname_nsprefix_) else ''
            showIndent(outfile, level, pretty_print)
            outfile.write('<%sfirstname>%s</%sfirstname>%s' % (namespaceprefix_ , self.gds_encode(self.gds_format_string(quote_xml(self.firstname), input_name='firstname')), namespaceprefix_ , eol_))
        if self.lastname is not None:
            namespaceprefix_ = self.lastname_nsprefix_ + ':' if (UseCapturedNS_ and self.lastname_nsprefix_) else ''
            showIndent(outfile, level, pretty_print)
            outfile.write('<%slastname>%s</%slastname>%s' % (namespaceprefix_ , self.gds_encode(self.gds_format_string(quote_xml(self.lastname), input_name='lastname')), namespaceprefix_ , eol_))
        if self.other_name is not None:
            namespaceprefix_ = self.other_name_nsprefix_ + ':' if (UseCapturedNS_ and self.other_name_nsprefix_) else ''
            showIndent(outfile, level, pretty_print)
            outfile.write('<%sother-name>%s</%sother-name>%s' % (namespaceprefix_ , self.gds_format_float(self.other_name, input_name='other-name'), namespaceprefix_ , eol_))
        if self.class_ is not None:
            namespaceprefix_ = self.class__nsprefix_ + ':' if (UseCapturedNS_ and self.class__nsprefix_) else ''
            showIndent(outfile, level, pretty_print)
            outfile.write('<%sclass>%s</%sclass>%s' % (namespaceprefix_ , self.gds_format_float(self.class_, input_name='class'), namespaceprefix_ , eol_))
        for other_value_ in self.other_value:
            namespaceprefix_ = self.other_value_nsprefix_ + ':' if (UseCapturedNS_ and self.other_value_nsprefix_) else ''
            showIndent(outfile, level, pretty_print)
            outfile.write('<%sother-value>%s</%sother-value>%s' % (namespaceprefix_ , self.gds_format_float(other_value_, input_name='other-value'), namespaceprefix_ , eol_))
        for type_ in self.type_:
            namespaceprefix_ = self.type__nsprefix_ + ':' if (UseCapturedNS_ and self.type__nsprefix_) else ''
            showIndent(outfile, level, pretty_print)
            outfile.write('<%stype>%s</%stype>%s' % (namespaceprefix_ , self.gds_format_float(type_, input_name='type'), namespaceprefix_ , eol_))
        for client_handler_ in self.client_handler:
            namespaceprefix_ = self.client_handler_nsprefix_ + ':' if (UseCapturedNS_ and self.client_handler_nsprefix_) else ''
            client_handler_.export(outfile, level, namespaceprefix_, namespacedef_='', name_='client-handler', pretty_print=pretty_print)
    def exportLiteral(self, outfile, level, name_='booster'):
        level += 1
        already_processed = set()
        self._exportLiteralAttributes(outfile, level, already_processed, name_)
        if self._hasContent():
            self._exportLiteralChildren(outfile, level, name_)
    def _exportLiteralAttributes(self, outfile, level, already_processed, name_):
        pass
    def _exportLiteralChildren(self, outfile, level, name_):
        if self.firstname is not None:
            showIndent(outfile, level)
            outfile.write('firstname=%s,\n' % self.gds_encode(quote_python(self.firstname)))
        if self.lastname is not None:
            showIndent(outfile, level)
            outfile.write('lastname=%s,\n' % self.gds_encode(quote_python(self.lastname)))
        if self.other_name is not None:
            showIndent(outfile, level)
            outfile.write('other_name=%f,\n' % self.other_name)
        if self.class_ is not None:
            showIndent(outfile, level)
            outfile.write('class_=%f,\n' % self.class_)
        showIndent(outfile, level)
        outfile.write('other_value=[\n')
        level += 1
        for other_value_ in self.other_value:
            showIndent(outfile, level)
            outfile.write('%f,\n' % other_value_)
        level -= 1
        showIndent(outfile, level)
        outfile.write('],\n')
        showIndent(outfile, level)
        outfile.write('type_=[\n')
        level += 1
        for type_ in self.type_:
            showIndent(outfile, level)
            outfile.write('%f,\n' % type_)
        level -= 1
        showIndent(outfile, level)
        outfile.write('],\n')
        showIndent(outfile, level)
        outfile.write('client_handler=[\n')
        level += 1
        for client_handler_ in self.client_handler:
            showIndent(outfile, level)
            outfile.write('model_.client_handlerType(\n')
            client_handler_.exportLiteral(outfile, level, name_='client-handlerType')
            showIndent(outfile, level)
            outfile.write('),\n')
        level -= 1
        showIndent(outfile, level)
        outfile.write('],\n')
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
    def walk_and_update(self):
        members = booster._member_data_items
        for member in members:
            obj1 = getattr(self, member.get_name())
            if member.get_data_type() == 'xs:date':
                newvalue = date_calcs.date_from_string(obj1)
                setattr(self, member.get_name(), newvalue)
            elif member.get_container():
                for child in obj1:
                    if type(child) == types.InstanceType:
                        child.walk_and_update()
            else:
                obj1 = getattr(self, member.get_name())
                if type(obj1) == types.InstanceType:
                    obj1.walk_and_update()
        if booster.superclass != None:
          booster.superclass.walk_and_update(self)
    def walk_and_show(self, depth):
        global counter
        counter += 1
        depth += 1
        print('%d. class: booster  depth: %d' % (counter, depth, ))
        members = booster._member_data_items
        for member in members:
            s1 = member.get_name()
            s2 = member.get_data_type()
            s3 = '%d' % member.get_container()
            obj1 = getattr(self, member.get_name())
            if member.get_container():
                s4 = '<container>'
            else:
                if type(obj1) != types.InstanceType:
                    s4 = '%s' % obj1
                else:
                    s4 = '<instance>'
            s5 = '%s%s%s  %s' % (s1.ljust(16), s2.ljust(16), s3.rjust(4), s4, )
            print('   ', s5)
        for member in members:
            if member.get_container():
                for child in getattr(self, member.get_name()):
                    if type(child) == types.InstanceType:
                        child.walk_and_show(depth)
            else:
                obj1 = getattr(self, member.get_name())
                if type(obj1) == types.InstanceType:
                    obj1.walk_and_show(depth)
# end class booster


class info(GeneratedsSuper):
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
                CurrentSubclassModule_, info)
            if subclass is not None:
                return subclass(*args_, **kwargs_)
        if info.subclass:
            return info.subclass(*args_, **kwargs_)
        else:
            return info(*args_, **kwargs_)
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
    def export(self, outfile, level, namespaceprefix_='', namespacedef_='', name_='info', pretty_print=True):
        imported_ns_def_ = GenerateDSNamespaceDefs_.get('info')
        if imported_ns_def_ is not None:
            namespacedef_ = imported_ns_def_
        if pretty_print:
            eol_ = '\n'
        else:
            eol_ = ''
        if self.original_tagname_ is not None and name_ == 'info':
            name_ = self.original_tagname_
        if UseCapturedNS_ and self.ns_prefix_:
            namespaceprefix_ = self.ns_prefix_ + ':'
        showIndent(outfile, level, pretty_print)
        outfile.write('<%s%s%s' % (namespaceprefix_, name_, namespacedef_ and ' ' + namespacedef_ or '', ))
        already_processed = set()
        self._exportAttributes(outfile, level, already_processed, namespaceprefix_, name_='info')
        if self._hasContent():
            outfile.write('>%s' % (eol_, ))
            self._exportChildren(outfile, level + 1, namespaceprefix_, namespacedef_, name_='info', pretty_print=pretty_print)
            outfile.write('</%s%s>%s' % (namespaceprefix_, name_, eol_))
        else:
            outfile.write('/>%s' % (eol_, ))
    def _exportAttributes(self, outfile, level, already_processed, namespaceprefix_='', name_='info'):
        if self.name is not None and 'name' not in already_processed:
            already_processed.add('name')
            outfile.write(' name=%s' % (self.gds_encode(self.gds_format_string(quote_attrib(self.name), input_name='name')), ))
        if self.type_ is not None and 'type_' not in already_processed:
            already_processed.add('type_')
            outfile.write(' type="%s"' % self.gds_format_integer(self.type_, input_name='type'))
        if self.rating is not None and 'rating' not in already_processed:
            already_processed.add('rating')
            outfile.write(' rating="%s"' % self.gds_format_float(self.rating, input_name='rating'))
    def _exportChildren(self, outfile, level, namespaceprefix_='', namespacedef_='', name_='info', fromsubclass_=False, pretty_print=True):
        pass
    def exportLiteral(self, outfile, level, name_='info'):
        level += 1
        already_processed = set()
        self._exportLiteralAttributes(outfile, level, already_processed, name_)
        if self._hasContent():
            self._exportLiteralChildren(outfile, level, name_)
    def _exportLiteralAttributes(self, outfile, level, already_processed, name_):
        if self.name is not None and 'name' not in already_processed:
            already_processed.add('name')
            showIndent(outfile, level)
            outfile.write('name="%s",\n' % (self.name,))
        if self.type_ is not None and 'type_' not in already_processed:
            already_processed.add('type_')
            showIndent(outfile, level)
            outfile.write('type_=%d,\n' % (self.type_,))
        if self.rating is not None and 'rating' not in already_processed:
            already_processed.add('rating')
            showIndent(outfile, level)
            outfile.write('rating=%f,\n' % (self.rating,))
    def _exportLiteralChildren(self, outfile, level, name_):
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
    def walk_and_update(self):
        members = info._member_data_items
        for member in members:
            obj1 = getattr(self, member.get_name())
            if member.get_data_type() == 'xs:date':
                newvalue = date_calcs.date_from_string(obj1)
                setattr(self, member.get_name(), newvalue)
            elif member.get_container():
                for child in obj1:
                    if type(child) == types.InstanceType:
                        child.walk_and_update()
            else:
                obj1 = getattr(self, member.get_name())
                if type(obj1) == types.InstanceType:
                    obj1.walk_and_update()
        if info.superclass != None:
          info.superclass.walk_and_update(self)
    def walk_and_show(self, depth):
        global counter
        counter += 1
        depth += 1
        print('%d. class: info  depth: %d' % (counter, depth, ))
        members = info._member_data_items
        for member in members:
            s1 = member.get_name()
            s2 = member.get_data_type()
            s3 = '%d' % member.get_container()
            obj1 = getattr(self, member.get_name())
            if member.get_container():
                s4 = '<container>'
            else:
                if type(obj1) != types.InstanceType:
                    s4 = '%s' % obj1
                else:
                    s4 = '<instance>'
            s5 = '%s%s%s  %s' % (s1.ljust(16), s2.ljust(16), s3.rjust(4), s4, )
            print('   ', s5)
        for member in members:
            if member.get_container():
                for child in getattr(self, member.get_name()):
                    if type(child) == types.InstanceType:
                        child.walk_and_show(depth)
            else:
                obj1 = getattr(self, member.get_name())
                if type(obj1) == types.InstanceType:
                    obj1.walk_and_show(depth)
# end class info


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
    def export(self, outfile, level, namespaceprefix_='', namespacedef_='', name_='client-handlerType', pretty_print=True):
        imported_ns_def_ = GenerateDSNamespaceDefs_.get('client-handlerType')
        if imported_ns_def_ is not None:
            namespacedef_ = imported_ns_def_
        if pretty_print:
            eol_ = '\n'
        else:
            eol_ = ''
        if self.original_tagname_ is not None and name_ == 'client-handlerType':
            name_ = self.original_tagname_
        if UseCapturedNS_ and self.ns_prefix_:
            namespaceprefix_ = self.ns_prefix_ + ':'
        showIndent(outfile, level, pretty_print)
        outfile.write('<%s%s%s' % (namespaceprefix_, name_, namespacedef_ and ' ' + namespacedef_ or '', ))
        already_processed = set()
        self._exportAttributes(outfile, level, already_processed, namespaceprefix_, name_='client-handlerType')
        if self._hasContent():
            outfile.write('>%s' % (eol_, ))
            self._exportChildren(outfile, level + 1, namespaceprefix_, namespacedef_, name_='client-handlerType', pretty_print=pretty_print)
            showIndent(outfile, level, pretty_print)
            outfile.write('</%s%s>%s' % (namespaceprefix_, name_, eol_))
        else:
            outfile.write('/>%s' % (eol_, ))
    def _exportAttributes(self, outfile, level, already_processed, namespaceprefix_='', name_='client-handlerType'):
        pass
    def _exportChildren(self, outfile, level, namespaceprefix_='', namespacedef_='', name_='client-handlerType', fromsubclass_=False, pretty_print=True):
        if pretty_print:
            eol_ = '\n'
        else:
            eol_ = ''
        if self.fullname is not None:
            namespaceprefix_ = self.fullname_nsprefix_ + ':' if (UseCapturedNS_ and self.fullname_nsprefix_) else ''
            showIndent(outfile, level, pretty_print)
            outfile.write('<%sfullname>%s</%sfullname>%s' % (namespaceprefix_ , self.gds_encode(self.gds_format_string(quote_xml(self.fullname), input_name='fullname')), namespaceprefix_ , eol_))
        if self.refid is not None:
            namespaceprefix_ = self.refid_nsprefix_ + ':' if (UseCapturedNS_ and self.refid_nsprefix_) else ''
            showIndent(outfile, level, pretty_print)
            outfile.write('<%srefid>%s</%srefid>%s' % (namespaceprefix_ , self.gds_format_integer(self.refid, input_name='refid'), namespaceprefix_ , eol_))
    def exportLiteral(self, outfile, level, name_='client-handlerType'):
        level += 1
        already_processed = set()
        self._exportLiteralAttributes(outfile, level, already_processed, name_)
        if self._hasContent():
            self._exportLiteralChildren(outfile, level, name_)
    def _exportLiteralAttributes(self, outfile, level, already_processed, name_):
        pass
    def _exportLiteralChildren(self, outfile, level, name_):
        if self.fullname is not None:
            showIndent(outfile, level)
            outfile.write('fullname=%s,\n' % self.gds_encode(quote_python(self.fullname)))
        if self.refid is not None:
            showIndent(outfile, level)
            outfile.write('refid=%d,\n' % self.refid)
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
    def walk_and_update(self):
        members = client_handlerType._member_data_items
        for member in members:
            obj1 = getattr(self, member.get_name())
            if member.get_data_type() == 'xs:date':
                newvalue = date_calcs.date_from_string(obj1)
                setattr(self, member.get_name(), newvalue)
            elif member.get_container():
                for child in obj1:
                    if type(child) == types.InstanceType:
                        child.walk_and_update()
            else:
                obj1 = getattr(self, member.get_name())
                if type(obj1) == types.InstanceType:
                    obj1.walk_and_update()
        if client_handlerType.superclass != None:
          client_handlerType.superclass.walk_and_update(self)
    def walk_and_show(self, depth):
        global counter
        counter += 1
        depth += 1
        print('%d. class: client_handlerType  depth: %d' % (counter, depth, ))
        members = client_handlerType._member_data_items
        for member in members:
            s1 = member.get_name()
            s2 = member.get_data_type()
            s3 = '%d' % member.get_container()
            obj1 = getattr(self, member.get_name())
            if member.get_container():
                s4 = '<container>'
            else:
                if type(obj1) != types.InstanceType:
                    s4 = '%s' % obj1
                else:
                    s4 = '<instance>'
            s5 = '%s%s%s  %s' % (s1.ljust(16), s2.ljust(16), s3.rjust(4), s4, )
            print('   ', s5)
        for member in members:
            if member.get_container():
                for child in getattr(self, member.get_name()):
                    if type(child) == types.InstanceType:
                        child.walk_and_show(depth)
            else:
                obj1 = getattr(self, member.get_name())
                if type(obj1) == types.InstanceType:
                    obj1.walk_and_show(depth)
# end class client_handlerType


GDSClassesMapping = {
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
        rootTag = 'people'
        rootClass = people
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
        rootTag = 'people'
        rootClass = people
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
        rootTag = 'people'
        rootClass = people
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
        rootTag = 'people'
        rootClass = people
    rootObj = rootClass.factory()
    rootObj.build(rootNode, gds_collector_=gds_collector)
    # Enable Python to collect the space used by the DOM.
    if not SaveElementTreeNode:
        doc = None
        rootNode = None
    if not silence:
        sys.stdout.write('#from out2_sup import *\n\n')
        sys.stdout.write('import out2_sup as model_\n\n')
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
    "agent",
    "booster",
    "client_handlerType",
    "comments",
    "info",
    "java_programmer",
    "param",
    "people",
    "person",
    "programmer",
    "python_programmer",
    "special_agent"
]
