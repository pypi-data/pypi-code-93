import json

import cro_validate.api.definition_api as DefinitionApi
import cro_validate.api.exception_api as ExceptionApi
import cro_validate.api.example_api as ExampleApi
import cro_validate.classes.rule_classes as Rules
import cro_validate.input.normalize_input as NormalizeInput
import cro_validate.classes.schema_classes as Schemas
from cro_validate.enum import DataType


DefinitionApi.clear()

class Boolean(Rules.Rule):
	def _as_bool(self, name, value):
		# Int must be 1 or 0
		try:
			int_value = NormalizeInput.as_int_within_inclusive_range(name, value, 0, 1)
			if int_value == 0:
				return False
			if int_value == 1:
				return True
		except:
			pass
		# String must be True or False (case insensitive)
		str_value = str(value)
		if str_value.lower() == 'true':
			return True
		if str_value.lower() == 'false':
			return False
		msg = "Expected to be 'True' or 'False' (case insensitive), not ['{0}'].".format(value)
		raise ExceptionApi.create_input_error(name, msg)

	def __init__(self):
		super().__init__(
				description='Must be one of 0, 1, True, False (case insensitive).',
				callback=self._as_bool
			)


class TestModel:
	a = None
	b = Schemas.Field(input_name='b', required=False)


def register():
	DefinitionApi.clear()

	DefinitionApi.register_definition(
			name='a',
			data_type=DataType.Boolean,
			default_value=False,
			rules=[Boolean()]
		)

	DefinitionApi.register_definition(
			name='b',
			data_type=DataType.Boolean,
			default_value=False,
			rules=[Boolean()]
		)

	DefinitionApi.register_definition(
			data_type=DataType.Object,
			data_format=Schemas.Schema(TestModel)
		)

	DefinitionApi.register_definition(
			data_type=DataType.Array,
			data_format='TestModel'
		)


def test__simple_array__validation():
	register()
	v = {'a':True}
	result = DefinitionApi.validate_input('TestModel', v)


def test__simple_array__object_generation():
	register()
	v = {'a':[True, 100], 'b':[False, -1]}
	result = []
	for example in ExampleApi.get_example_generator('TestModel', given_values=v):
		print(json.dumps(example, indent=2, sort_keys=True))
		result.append(example)
	assert len(result) == 3


def test__simple_array__array_generation():
	register()
	v = [
			{'a':[True, 100], 'b':[False, -1]}
		]
	result = []
	for example in ExampleApi.get_example_generator('TestModelArray', given_values=v):
		print(json.dumps(example, indent=2, sort_keys=True))
		result.append(example)
	assert len(result) == 3


def test__simple_array__array_generation_with_optional_value():
	register()
	v = [
			{'a':[True, 100]}
		]
	result = []
	for example in ExampleApi.get_example_generator('TestModelArray', given_values=v):
		print(json.dumps(example, indent=2, sort_keys=True))
		result.append(example)
	assert len(result) == 2
