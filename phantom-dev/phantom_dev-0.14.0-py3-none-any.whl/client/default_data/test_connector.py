from logging import getLogger
from tempfile import TemporaryDirectory
from unittest import mock

from pytest import fixture, fail

from connector import Choice, Connector


logger = getLogger(name=__name__)


NULL_VALUE = object()


@fixture(params=[42, 69, 13.37, -5, 0])
def numeric_value(request):
	return float(request.param)

@fixture(params=['foo', 'bar', 'baz'])
def text_value(request):
	return request.param

@fixture(params=[True, False])
def bool_value(request):
	return request.param

@fixture(params=Choice)
def choice_value(request):
	if request.param is NULL_VALUE:
		return request.param

	return request.param.value

@fixture(params=[NULL_VALUE, 420.69])
def optional_numeric(request):
	return request.param

@fixture(params=[NULL_VALUE, 'optional'])
def optional_text(request, text_value):
	return request.param

@fixture(params=[NULL_VALUE, True, False])
def optional_bool(request, text_value):
	return request.param

@fixture(params=[NULL_VALUE, *Choice])
def optional_choice(request):
	if request.param is NULL_VALUE:
		return request.param

	return request.param.value

@fixture
def expected_result(
		request,
		numeric_value,
		text_value,
		bool_value,
		choice_value,
		optional_numeric,
		optional_text,
		optional_bool,
		optional_choice,
):
	if optional_numeric is NULL_VALUE:
		optional_numeric = 42.69

	if optional_text is NULL_VALUE:
		optional_text = 'spam'

	if optional_bool is NULL_VALUE:
		optional_bool = False

	if optional_choice is NULL_VALUE:
		optional_choice = None

	return [
		{
			'name': 'required_number',
			'value': numeric_value,
			'type': 'float',
			'context': 'None',
		},
		{
			'name': 'required_str',
			'value': text_value,
			'type': 'str',
			'context': 'None',
		},
		{
			'name': 'required_bool',
			'value': bool_value,
			'type': 'bool',
			'context': 'None',
		},
		{
			'name': 'required_choice',
			'value': choice_value,
			'type': 'str',
			'context': 'None',
		},
		{
			'name': 'optional_number',
			'value': optional_numeric,
			'type': 'float',
			'context': 'None',
		},
		{
			'name': 'optional_str',
			'value': optional_text,
			'type': 'str',
			'context': 'None',
		},
		{
			'name': 'optional_bool',
			'value': optional_bool,
			'type': 'bool',
			'context': 'None',
		},
		{
			'name': 'optional_choice',
			'value': optional_choice,
			'type': 'NoneType' if optional_choice is None else 'str',
			'context': 'None',
		},
	]

@fixture
def get_state_dir():
	with TemporaryDirectory() as tmp_dir:
		yield lambda _: tmp_dir

@fixture
def connector(get_state_dir):
	with mock.patch.object(Connector, 'get_state_dir', get_state_dir):
		connector = Connector()
		with mock.patch.object(connector, 'logger', logger):
			yield connector


def test_dummy_action(
		connector,
		numeric_value,
		text_value,
		bool_value,
		choice_value,
		optional_numeric,
		optional_text,
		optional_bool,
		optional_choice,
		expected_result,
):
	sort_key = lambda x: x['name']
	optionals = {
		'optional_number': optional_numeric,
		'optional_str': optional_text,
		'optional_bool': optional_bool,
		'optional_choice': optional_choice,
	}
	optionals = {k: v for k, v in optionals.items() if v is not NULL_VALUE}
	state = {}
	with mock.patch.object(Connector, 'state', state):
		result = list(connector.dummy_action(
			numeric_value, text_value, bool_value, choice_value, **optionals))

	sorted_result = sorted(result, key=sort_key)
	sorted_expected_result = sorted(expected_result, key=sort_key)
	assert sorted_result == sorted_expected_result
	assert state['last_data'] == result[-1]


def test_dummy_async(connector):
	concurrency = 100
	sleep = 0.1
	with mock.patch.object(
			connector, 'get_action_identifier', lambda: 'dummy_async'):
		connector.handle_action({'concurrency': concurrency, 'sleep': sleep})

	result, = connector.get_action_results()
	result_data = result.get_data()
	assert len(result_data) == concurrency
	result_summary = result.get_summary()
	assert result_summary['count'] == concurrency
