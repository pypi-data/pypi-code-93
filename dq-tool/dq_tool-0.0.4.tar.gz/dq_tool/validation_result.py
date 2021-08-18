"""Functions for working with validation result - the stuff that comes out of dq_tool.validate"""

from typing import List, Dict
import json
import string
import dateutil.parser

from great_expectations.core import ExpectationConfiguration
from great_expectations.render.renderer.content_block import ExpectationStringRenderer

from .misc.printing import yamlize
from .expectation_attributes.expectation import Expectation
from .expressions import Expressions
from .misc.printing import pretty_repr


class ValidationResult:
    """A class for pretty printing validation results"""
    def __init__(self, dq_tool: 'DQTool', result: dict):
        self._result = result
        self._dq_tool = dq_tool
        self._spark_df = None

    # GE object for rendering definitions into human-readable strings
    _renderer = ExpectationStringRenderer()

    @property
    def success(self):
        """Was the validation successful?"""
        return self._result['success']

    def to_dict(self) -> Dict:
        """Dictionary - what came from GE"""
        return self._result

    _SPARK_DF_SCHEMA_DICT = {
        'type': 'struct',
        'fields': [
            {'name': 'run_time', 'type': 'timestamp', 'nullable': True, 'metadata': {}},
            {'name': 'definition_str', 'type': 'string', 'nullable': True, 'metadata': {}},
            {'name': 'expectation_suite_name', 'type': 'string', 'nullable': True, 'metadata': {}},
            {'name': 'expectation_type', 'type': 'string', 'nullable': True, 'metadata': {}},
            {'name': 'success', 'type': 'boolean', 'nullable': True, 'metadata': {}},
            {'name': 'column', 'type': 'string', 'nullable': True, 'metadata': {}},
            {
                'name': 'result_details',
                'type': {
                    'type': 'struct',
                    'fields': [
                        {'name': 'observed_value_str', 'type': 'string', 'nullable': True, 'metadata': {}},
                        {'name': 'element_count', 'type': 'long', 'nullable': True, 'metadata': {}},
                        {'name': 'missing_count', 'type': 'long', 'nullable': True, 'metadata': {}},
                        {'name': 'missing_percent', 'type': 'double', 'nullable': True, 'metadata': {}}
                    ]
                },
                'nullable': True,
                'metadata': {}
            },
            {
                'name': 'fail_details',
                'type': {
                    'type': 'struct',
                    'fields': [
                        {'name': 'unexpected_count', 'type': 'long', 'nullable': True, 'metadata': {}},
                        {'name': 'unexpected_percent', 'type': 'double', 'nullable': True, 'metadata': {}},
                        {'name': 'unexpected_percent_nonmissing', 'type': 'double', 'nullable': True, 'metadata': {}},
                        {
                            'name': 'partial_unexpected_list_str',
                            'type': {
                                'type': 'array',
                                'elementType': 'string',
                                'containsNull': True
                            },
                            'nullable': True,
                            'metadata': {}
                        },
                        {
                            'name': 'exception_info',
                            'type': {
                                'type': 'struct',
                                'fields': [
                                    {'name': 'raised_exception', 'type': 'boolean', 'nullable': True, 'metadata': {}},
                                    {'name': 'exception_message', 'type': 'string', 'nullable': True, 'metadata': {}},
                                    {'name': 'exception_traceback', 'type': 'string', 'nullable': True, 'metadata': {}},

                                ]
                            },
                            'nullable': True,
                            'metadata': {}
                        }
                    ]
                },
                'nullable': True,
                'metadata': {}
            },
            {'name': 'validation_result_json', 'type': 'string', 'nullable': True, 'metadata': {}}
        ]
    }

    def to_spark_df(self) -> 'DataFrame':
        """Spark dataframe with a line for each  expectation that has run"""
        if self._spark_df:
            return self._spark_df
        df_data = self._get_spark_df_data()
        schema = self._dq_tool._get_struct_schema(self._SPARK_DF_SCHEMA_DICT)  # pylint: disable=W0212
        return self._dq_tool._spark.createDataFrame(  # pylint: disable=W0212
            data=df_data,
            schema=schema
        )

    @classmethod
    def _str_or_none(cls, d: dict, key: str) -> str:
        """Get a string representation of a value in d, None if it's not there"""
        val = d.get(key)
        if not val:
            return None
        return str(val)

    @classmethod
    def _filter_out_none_values(cls, d: Dict) -> Dict:
        """Takes a dict keeps only keys that have non-None value, if nothing's left returns none"""
        filtered = {k: v for k, v in d.items() if v is not None}
        return filtered or None

    @classmethod
    def _extract_result_details(cls, result: Dict) -> Dict:
        """Get result details out of the whole result dict"""
        res = result['result']
        return cls._filter_out_none_values({
            'observed_value_str': cls._str_or_none(res, 'observed_value'),
            'element_count': res.get('element_count'),
            'missing_count': res.get('missing_count'),
            'missing_percent': res.get('missing_percent')
        })

    @classmethod
    def _extract_exception_info(cls, result: Dict) -> Dict:
        """Get exception_info out of the whole result dict, None if there was no exception"""
        if 'exception_info' not in result:
            return None
        exinfo = result['exception_info']
        raised = exinfo.get('raised_exception')
        if not raised:
            return None
        return cls._filter_out_none_values({
            'raised_exception': raised,
            'exception_message': cls._str_or_none(exinfo, 'exception_message'),
            'exception_traceback': cls._str_or_none(exinfo, 'exception_traceback')
        })

    @classmethod
    def _extract_fail_details(cls, result: Dict) -> Dict:
        """Get fail details for a fail result"""
        if result['success']:
            return None
        return cls._filter_out_none_values({
            'unexpected_count': result['result'].get('unexpected_count'),
            'unexpected_percent': result['result'].get('unexpected_percent'),
            'unexpected_percent_nonmissing': result['result'].get('unexpected_percent_nonmissing'),
            'partial_unexpected_list_str': [
                str(u) for u in result['result']['partial_unexpected_list']
            ] if 'partial_unexpected_list' in result['result'] else None,
            'exception_info': cls._extract_exception_info(result)
        })

    @classmethod
    def _render_definition_str(cls, result: Dict) -> str:
        """Render a human-readable string describing the expectation definition"""

        # create an ExpectationConfiguration from the result
        config_dict = result['expectation_config']
        if Expressions.is_expression(config_dict['expectation_type']):
            # for the purpose of string rendering change the type to basic expression
            config_dict['expectation_type'] = Expressions.expression_to_basic(config_dict['expectation_type'])
            # for expectations with expressions, add the column_expression* also as column*
            non_expression_kwargs = {
                Expressions.expression_to_basic(k): v
                for k, v in config_dict['kwargs'].items()
                if Expressions.is_expression(k)
            }
            config_dict['kwargs'].update(non_expression_kwargs)
        config = ExpectationConfiguration(**config_dict)

        # render the string
        render_results = cls._renderer.render(config)

        def_strings = []

        # iterate throught the results,
        # if it has .string_template use it. If it is a dict and has key 'string_template' use that
        for res in render_results:
            if hasattr(res, 'string_template'):
                # it's a simple expectation object
                template_dict = res.string_template
                def_strings.append(
                    string
                    .Template(template_dict['template'])
                    .substitute(template_dict['params'])
                )
                continue
            if isinstance(res, dict):
                res = dict(res)  # to make pylint quiet
                # it's a dict with string_template
                if 'string_template' in res:
                    def_strings.append(
                        string
                        .Template(res['string_template'].get('template', ''))
                        .substitute(res['string_template'].get('params', ''))
                    )
                    continue
                    # otherwise some tables are involved
                def_strings.append(' '.join([
                    str(res.get('header_row')),
                    str(res.get('table'))
                ]))
        return ' '.join(c for c in def_strings if c)

    def _get_spark_df_data(self) -> List:
        run_time = dateutil.parser.parse(self._result['meta']['run_id']['run_time'])
        expectation_suite_name = self._result['meta']['expectation_suite_name']
        return [
            (
                run_time,  # run_time
                self._render_definition_str(r),  # definition_str
                expectation_suite_name,  # expectation_suite_name
                r['expectation_config']['expectation_type'],  # expectation_type
                r['success'],  # success
                r['expectation_config']['kwargs'].get('column'),  # column
                self._extract_result_details(r),  # result_details
                self._extract_fail_details(r),  # fail_details
                json.dumps(r)  # validation_result_json
            ) for r in self._result['results']
        ]

    def __repr__(self) -> str:
        """Pretty printed result dict"""
        return pretty_repr(self._result)

    def __str__(self) -> str:
        """Yaml-like output for expectations and their results"""
        # put together a dict with results and yamlize
        # next up: group the results by table/column and by column as in suites
        str_dict = {
            **{
                'success': self.success,
                'expectation_suite_name': self._result['meta'].get('expectation_suite_name'),
                # success: call_str for each expectation
                'results': [
                    '{}: {}'.format(json.dumps(res['success']), Expectation(res['expectation_config']).call_str)
                    for res in self._result['results']
                ]
            }
        }
        return yamlize(str_dict)
