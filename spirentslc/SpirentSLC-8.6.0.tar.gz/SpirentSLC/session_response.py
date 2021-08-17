# ****************       BEGIN-STANDARD-COPYRIGHT      ***************
#
# Copyright (c) 2017, Spirent Communications.
#
# All rights reserved. Proprietary and confidential information of Spirent Communications.
#
#  ***************        END-STANDARD-COPYRIGHT       ***************

"""Session profile class and necessary tools."""

import re
import six
import sys
import json

from lxml import etree
from contextlib import contextmanager
from functools import cmp_to_key

try:
    from collections.abc import Iterable
except ImportError:
    from collections import Iterable

if six.PY2:
    from exceptions import SyntaxError
else:
    from builtins import SyntaxError

if six.PY2:
    import codecs

if six.PY2:
    from cStringIO import StringIO
else:
    from io import StringIO

from .internal import ExecutionProtocol_pb2 as pb

_DEBUG = False

_RESULT_MESSAGE = {
    pb.SUCCESS: 'success',
    pb.ABORTED: 'aborted',
    pb.TIMEOUT: 'timeout',
    pb.FAILED: 'failed',
    pb.SKIPPED: 'skipped'
}

_FIRST_CAP_RE = re.compile('(.)([A-Z][a-z]+)')
_ALL_CAP_RE = re.compile('([a-z0-9])([A-Z])')
_CAP2_PLUS = re.compile('(_)(_+)')

_PYTHON_KEYWORDS = {
    'and',
    'del',
    'from',
    'not',
    'while',
    'as',
    'elif',
    'global',
    'or',
    'with',
    'assert',
    'else',
    'if',
    'pass',
    'yield',
    'break',
    'except',
    'import',
    'print',
    'class',
    'exec',
    'in',
    'raise',
    'continue',
    'finally',
    'is',
    'return',
    'def',
    'for',
    'lambda',
    'try'
}

_XPATH_SLC_NS_PREFIX = 'slc'
_XPATH_SLC_NS = 'slc-query-ns'

def getExecuionIssueSeverity(severity):
    return pb._EXECUTIONISSUEMESSAGE_SEVERITY.values_by_number[severity].name


def _to_snake_name(name):
    temp_var = _FIRST_CAP_RE.sub(r'\1_\2', name)
    res = _ALL_CAP_RE.sub(r'\1_\2', temp_var).lower()
    res = res.replace('-', '_')
    res = _CAP2_PLUS.sub(r'\1', res)
    return res


def ids_compare(id1, id2):
    if id1 == id2:
        return 0
    id1_set = id1.split(".")
    id2_set = id2.split(".")
    n = min(len(id1_set), len(id2_set))
    for idx in range(n):
        if int(id1_set[idx]) > int(id2_set[idx]):
            return 1
        if int(id1_set[idx]) < int(id2_set[idx]):
            return -1
    if len(id1_set) < len(id2_set):
        return -1
    else:
        return 1


def response_step_compare(step1, step2):
    return ids_compare(step1.id, step2.id)


class SessionActionResponse(object):
    """ A wrapper around a session action response """

    def __init__(self, message, nested_steps=(), execution_issues=[]):
        self.message = message
        self._nested_steps = tuple(nested_steps)
        self._execution_issues = execution_issues

        # Create dummy response body
        self._body = None

        # Create dummy structured data
        self._xml = etree.Element('structure')
        self._json_data = None
        self._xml_data = None
        # Need to convert all structured data to structure xml document
        self._prepare_structured_data()

        self._queries = {}
        try:
            if self.message.details != None:
                self._xpath_namespaces = {_XPATH_SLC_NS_PREFIX : _XPATH_SLC_NS}
                self._queries = {_to_snake_name(x.name): x for x in self.message.details.aliases}
                self._xpath_extensions = list(map(self._make_extension, self.message.details.aliases))
        except AttributeError:
            pass

    def _make_extension(self, alias):
        def function(context, *parameters):
            query = self._resolve_query(alias, parameters)
            return self._query(query)

        return {(_XPATH_SLC_NS, alias.name): function}

    def _prepare_structured_data(self):
        if not hasattr(self.message, 'details') or self.message.details is None:
            return

        mapped = None
        parser = etree.XMLParser(remove_blank_text=True)
        for s in self.message.details.structuredData:
            if '*' == s.map:
                for item in s.items:
                    self._item_to_element(self._xml, item)

            else:
                if mapped is None:
                    mapped = etree.SubElement(self._xml, 'mapped')

                for item in s.items:
                    if item.name == 'json':
                        self._json_data = json.loads(self.message.details.body)
                    elif item.name == 'xml':
                        try:
                            self._xml_data = etree.XML(item.value.encode('utf-8'), parser)
                        except SyntaxError as err:
                            print('xml response parse error:', err)

                    # every value item here is stored XML, so we need to parse it from this items
                    mapped_child = etree.XML(item.value.encode('utf-8'), parser)
                    mapped.append(mapped_child)

    def steps_report(self):
        def step_report(msg, ns=True, executed_issues=[]):
            step_name = "Nested Step" if ns else "QuickCall"
            step_rep = u"\n{0} {1}" \
                       u"\n------------------------------------------------------" \
                       u"\nAction: \t{2}" \
                       u"\nCommand: \t{4}" \
                       u"\nDuration: \t{3}" \
                       u"\nExecution issues:\t{6}" \
                       u"\nBody:\n{5}\n"
            nd = msg.nestedActionDetails
            exec_issues = [(getExecuionIssueSeverity(issue.severity), str(issue.message)) for issue in executed_issues]
            return step_rep.format(step_name, nd.stepId, nd.action.action, msg.duration,
                                   nd.action.command, msg.details.body, exec_issues)

        def traverse_tree(step):
            res = u""
            for st in step.nested_steps:
                res += step_report(st.message, executed_issues=st.issues)
                res += traverse_tree(st)
            return res

        report = step_report(self.message, False, self._execution_issues) + traverse_tree(self)
        return report

    def _item_to_element(self, root, item):
        item_element = etree.SubElement(root, item.name)
        if len(item.items) > 0:
            for child_item in item.items:
                self._item_to_element(item_element, child_item)
        else:
            item_element.text = item.value

    def _result(self):
        """
            Return action response result
            May be 'success', 'failed', 'timeout', 'aborted', 'skipped'
        """
        res = _RESULT_MESSAGE[self.message.stepResult]
        if res is None:
            return 'unknown'
        return res

    def _text(self):
        """ return a text output of executed action """
        if self._body is None:
            if hasattr(self.message, 'details') and self.message.details != None:
                if six.PY2:
                    self._body = codecs.encode(self.message.details.body, 'utf-8')
                else:
                    self._body = self.message.details.body
            if self._body is None:
                self._body = ''

        return self._body

    def append_body(self, text_data):
        self._body = self._text() + text_data

    def __str__(self):
        return self._text()

    def __repr__(self):
        return self._text()

    def _structure(self):
        """ Return structured data of response"""
        return self.message.details.structuredData

    @property
    def duration(self):
        """ Return a step duration"""
        return self.message.duration

    def _post_processing(self):
        """ Return post processing data of response"""
        return self.message.details.postProcessing

    @property
    def structure(self):
        """ Return structured data of response"""
        return self._structure()

    @property
    def post_processing(self):
        """ Return post processing data of response"""
        return self._post_processing()

    @property
    def text(self):
        """ return a text output of executed action """
        return self._text()

    @property
    def json(self):
        """ return a json data"""
        return self._json_data

    @property
    def xml(self):
        """ return a xml data"""
        return self._xml_data

    def __getattr__(self, key):
        if key == 'text':
            return self._text()
        elif key == 'result':
            return self._result()
        elif key == 'structure':
            return self._structure()
        elif key == 'post_processing':
            return self._post_processing()
        elif key == 'json':
            return self._json_data
        elif key == 'xml':
            return self._xml_data
        elif key == 'data':
            return self.message.details.structuredData
        elif key == 'issues':
            return self._execution_issues
        else:
            ret = self[key]
            if ret != None:
                return ret
        raise AttributeError(key)

    def __getitem__(self, key):
        if key in self._queries:
            return lambda *args: self._invoke_query(key, *args)
        raise AttributeError(key)

    def _invoke_query(self, query_name, parameters=None):
        alias = self._queries[query_name]

        if _DEBUG:
            print("do query:", alias, " params: ", parameters)

        query = self._resolve_query(alias, parameters)
        if query != None:
            if _DEBUG:
                print("final query:", query)
            elements = self._xml.xpath(query)
            if len(elements) == 1:
                return elements[0].text
            elif len(elements) > 1:
                if isinstance(parameters, int):
                    return elements[int(parameters)].text
                else:
                    return [x.text for x in elements]

    def _resolve_query(self, alias, parameters):
        if alias != None and alias.queryFormat != None:
            query = alias.queryFormat

            # handle parameters
            if parameters != None and len(alias.arguments) > 0:

                # make sure parameters is a collection
                if not isinstance(parameters, Iterable) or isinstance(parameters, str):
                    parameters = (parameters,)  # convert to tuple

                # substitute parameters
                for i, param in enumerate(parameters):
                    query = query.replace('{' + str(i) + '}', str(param))

            # fix wrong '=' expressions
            query = query.replace(' =', '=')
            query = query.replace('= ', '=')
            return query

    def __dir__(self):
        """ return a list of methods available to project"""
        res = dir(super) + list(sorted(self._queries.keys()))
        return res

    def _query(self, query):
        return self._xml.xpath(query, namespaces=self._xpath_namespaces, extensions=self._xpath_extensions)

    def query(self, query):
        """ return a result of xpath query evaluation on structured response"""
        elements = self._query(_XPATH_SLC_NS_PREFIX + ':' + query)
        if isinstance(elements, Iterable) and not elements:
            elements = self._query(query)

        if not isinstance(elements, Iterable) or isinstance(elements, str):
            return elements
        if len(elements) == 1:
            return str.join('', next(iter(elements)).itertext())
        return [str.join('', el.itertext()) for el in elements]

    def queries(self):
        """
            Return a method names that query the structured data and return values.
            Queries may be auto-generated in iTest or be defined in response maps.
        """
        return self._get_queries(False)

    def query_strings(self):
        """
            Return a query strings for query function that query the structured data and return values.
            Queries may be auto-generated in iTest or be defined in response maps.
        """
        return self._get_queries(True)

    def _get_queries(self, is_string):
        res = '['
        first_time = True
        keys = sorted(self._queries.keys())
        for x in keys:
            if not is_string and x in _PYTHON_KEYWORDS:
                continue
            if first_time:
                first_time = False
            else:
                res += ', '
            msg = self._queries[x]
            res += '\'' + (msg.name if is_string else x) + '('
            first_time_child = True
            for arg in msg.arguments:
                if first_time_child:
                    first_time_child = False
                else:
                    res += ', '
                res += arg.name
            res += ')\''
        res += ']'
        return res

    @property
    def action(self):
        return self.message.nestedActionDetails.action

    @property
    def nested_steps(self):
        return self._nested_steps

    @property
    def id(self):
        return self.message.nestedActionDetails.step_id

    def add_nested(self, response):
        updated_steps = [step for step in self._nested_steps if step.id != response.id] + [response]
        self._nested_steps = tuple(sorted(updated_steps, key=cmp_to_key(response_step_compare)))


class DelegatingResponse(object):
    """A wrapper around captured response"""

    def __init__(self, slc, properties=None):
        self._slc = slc
        self._properties = properties
        self._delegate = None

    @contextmanager
    def capture(self):
        if self._delegate:
            raise ValueError("Response is already captured")
        parent_output = sys.stdout
        output_captor = StringIO()
        sys.stdout = output_captor
        try:
            yield
        except:
            raise
        finally:
            sys.stdout = parent_output
            value = output_captor.getvalue().rstrip('\n')
            output_captor.close()
            print(value)
            self._delegate = self._slc.response(value, properties=self._properties)

    def __getattr__(self, key):
        if not self._delegate:
            raise ValueError("Response is not captured yet")
        return getattr(self._delegate, key)
