from cro_validate.enum import DataType
import cro_validate.classes.definition_classes as Definitions
from cro_validate.classes.configuration_classes import Config
import cro_validate.classes.parameter_classes as Parameters
import cro_validate.classes.util_classes as Utils

class Schema:
	model = None
	model_name = None
	allow_unknown_fields = False
	return_unknown_fields = False
	display_name = None
	case_sensitive = True
	load_defaults = False
	dependency_resolver = None

	def __init__(
				self,
				model,
				model_name=Utils.Empty,
				allow_unknown_fields=Utils.Empty,
				display_name=Utils.Empty,
				case_sensitive=Utils.Empty,
				load_defaults=Utils.Empty,
				dependency_resolver=Utils.Empty,
				return_unknown_fields=Utils.Empty
			):
		def _set_member(name, value):
			if Utils.Empty.isempty(value):
				return
			setattr(self, name, value)
		if isinstance(model, type):
			model = model()
		elif isinstance(model, str):
			model = Definitions.Index.get(model).data_format.model
		_set_member('model', model)
		_set_member('model_name', model_name)
		_set_member('allow_unknown_fields', allow_unknown_fields)
		_set_member('display_name', display_name)
		_set_member('case_sensitive', case_sensitive)
		_set_member('load_defaults', load_defaults)
		_set_member('dependency_resolver', dependency_resolver)
		_set_member('return_unknown_fields', return_unknown_fields)
		if self.model_name is None:
			self.model_name = model.__class__.__name__

	def copy(self):
		result = Schema(
				model=self.model,
				model_name=self.model_name,
				allow_unknown_fields=self.allow_unknown_fields,
				display_name=self.display_name,
				case_sensitive=self.case_sensitive,
				load_defaults=self.load_defaults,
				dependency_resolver=self.dependency_resolver,
				return_unknown_fields=self.return_unknown_fields
			)
		return result

	def to_json_dict(self):
		def _is_default(name, value):
			if getattr(self.__class__, name) == value:
				return True
			return False
		def _set(target, name, value):
			if _is_default(name, value):
				return
			target[name] = value
		model = Utils.ClassName.class_fqn(self.model),
		model_type = 'DefinitionName'
		if not isinstance(self.model, str):
			model_type = 'SchemaDefinition'
			model = {}
			if isinstance(self.model, dict):
				for k in self.model:
					model[k] = self.model[k].to_json_dict(k)
			else:
				for entry in dir(self.model):
					if entry.startswith('_'):
						continue
					field = getattr(self.model, entry)
					if isinstance(field, Field):
						model[entry] = field.to_json_dict(entry)
					elif field is None:
						field = Field(input_name=entry)
						model[entry] = field.to_json_dict(entry)
		result = {
				'model_type': model_type
			}
		_set(result, 'model', model)
		_set(result, 'model_name', self.model_name)
		_set(result, 'allow_unknown_fields', self.allow_unknown_fields)
		_set(result, 'display_name', self.display_name)
		_set(result, 'case_sensitive', self.case_sensitive)
		return result


class Field:
	input_name = None
	output_name = None
	definition_name = None
	required = True
	ignored = False
	unvalidated = False
	default_value = Utils.Empty

	def __init__(
				self,
				input_name,
				output_name=Utils.Empty,
				definition_name=Utils.Empty,
				required=Utils.Empty,
				ignored=Utils.Empty,
				unvalidated=Utils.Empty,
				default_value=Utils.Empty
			):
		def _set_member(name, value):
			if Utils.Empty.isempty(value):
				return
			setattr(self, name, value)
		_set_member('input_name', input_name)
		_set_member('output_name', output_name)
		_set_member('definition_name', definition_name)
		_set_member('required', required)
		_set_member('ignored', ignored)
		_set_member('unvalidated', unvalidated)
		_set_member('default_value', default_value)
		if self.input_name is None:
			raise Exceptions.InternalError('Field', 'Input name must be specified')
		if self.output_name is None:
			self.output_name = self.input_name

	# Broken
	def to_json_dict(self, field_name):
		def _is_default(name, value):
			if getattr(self.__class__, name) == value:
				return True
			return False
		def _set(target, name, value):
			if _is_default(name, value):
				return
			target[name] = value
		default_value = self.default_value
		if Utils.Empty.isempty(self.default_value):
			default_value = None
		definition_name = self.definition_name
		if definition_name == field_name:
			definition_name = None
		result = {}
		if self.input_name != field_name:
			_set(result, 'input_name', self.input_name)
		_set(result, 'output_name', self.output_name)
		_set(result, 'definition_name', definition_name)
		_set(result, 'required', self.required)
		_set(result, 'ignored', self.ignored)
		_set(result, 'unvalidated', self.unvalidated)
		_set(result, 'dependency_resolver', self.dependency_resolver)
		_set(result, 'default_value', self.default_value)
		if 'default_value' in result:
			default_value_type = Utils.ClassName.class_fqn(self.default_value)
			result['default_value_type'] = default_value_type
		return result


class Validator:
	def _validate(self, validated, fqn, field_name, definition, value, **rules_kw):
		results = Parameters.Index.ensure(validated)
		cb = Definitions.Index.validate_input
		model_result = self.model_validator(None, fqn, field_name, definition, value, cb, **rules_kw)
		results[field_name] = model_result

	def __init__(self, name, model_validator):
		self.name = name
		self.model_validator = model_validator

	def __call__(self, results, fqn, field_name, definition, value, **rules_kw):
		return self._validate(results, fqn, field_name, definition, value, **rules_kw)

	def is_field_required(self, field_name):
		if field_name in self.model_validator.required:
			return True
		return False

	def get_field_definition_name(self, field_name):
		return self.model_validator.get_field_definition_name(field_name)

	def get_field_input_name(self, field_name):
		return self.model_validator.get_field_input_name(field_name)

	def get_field_input_display_name(self, field_name):
		return self.model_validator.get_field_input_display_name(field_name)

	def list_field_names(self):
		field_names = set()
		field_names.update(self.model_validator.required)
		field_names.update(self.model_validator.optional)
		return field_names

	def list_definition_names(self):
		field_names = set()
		field_names.update(self.model_validator.required)
		field_names.update(self.model_validator.optional)
		definition_names = set()
		for field_name in field_names:
			if field_name in self.model_validator.definition_names:
				definition_names.add(self.model_validator.definition_names[field_name])
			else:
				definition_names.add(field_name)
		field_names = definition_names
		object_names = set()
		results = set(field_names)
		for field_name in field_names:
			definition_name = field_name
			if definition_name in self.model_validator.definition_names:
				definition_name = self.model_validator.definition_names[field_name]
			field = Definitions.Index.get(definition_name)
			if field.data_type == DataType.Object:
				results.update(field.validator.list_definition_names())
				object_names.add(field_name)
			elif field.data_type == DataType.Array:
				pass
			else:
				pass
		for name in object_names:
			results.remove(name)
		return results


class ModelValidator:
	def __init__(self, schema):
		self.schema = schema
		self.required = set()
		self.optional = set()
		self.ignored = set()
		self.unvalidated = set()
		self.definition_names = {}
		self.input_field_names = {}
		self.input_value_names = {}
		self.default_values = {}
		self.input_field_display_names = {}
		self.output_names = {}
		self.output_value_names = {}
		self.dependency_order = []
		self.load_schema()
		self.name = schema.model_name
		if schema.display_name is not None:
			self.name = schema.display_name

	def add_required(self, names):
		self.required.update(names)

	def add_optional(self, names):
		self.optional.update(names)

	def add_ignored(self, names):
		self.ignored.update(names)

	def add_unvalidated(self, names):
		self.unvalidated.update(names)

	def add_definition_names(self, definition_names):
		self.definition_names.update(definition_names)

	def add_output_names(self, output_names):
		self.output_names.update(output_names)
		self.output_value_names.update({k:output_names[k] for k in output_names})

	def add_input_names(self, input_names):
		normalized = input_names
		if not self.schema.case_sensitive:
			normalized = {k.lower():input_names[k].lower() for k in input_names}
		self.input_field_display_names.update(input_names)
		self.input_field_names.update(normalized)
		self.input_value_names.update({normalized[k]:k for k in normalized})

	def add_default_values(self, default_values):
		for field_name in default_values:
			value = default_values[field_name]
			if Utils.Empty.isempty(value):
				continue
			self.default_values[field_name] = value

	def update_dependency_order(self):
		dependent_fields = set()
		independent_fields = set()
		for entry in self.definition_names:
			definition_name = self.definition_names[entry]
			definition = Definitions.Index.get(definition_name)
			if definition.is_one_of():
				dependent_fields.add(entry)
			else:
				independent_fields.add(entry)
		self.dependency_order = []
		self.dependency_order.extend(independent_fields)
		self.dependency_order.extend(dependent_fields)

	def add_spec(self,
				required,
				optional,
				ignored,
				unvalidated,
				definition_names={},
				input_names={},
				output_names={},
				default_values={}
			):
		if self.schema.case_sensitive:
			required = {k.lower() for k in required}
			optional = {k.lower() for k in optional}
			ignored = {k.lower() for k in ignored}
			unvalidated = {k.lower() for k in unvalidated}
			ignored = {k.lower() for k in ignored}
			default_values = {k.lower():default_values[k] for k in default_values}
		self.add_required(required)
		self.add_optional(optional)
		self.add_ignored(ignored)
		self.add_unvalidated(unvalidated)
		self.add_definition_names(definition_names)
		self.add_input_names(input_names)
		self.add_output_names(output_names)
		self.add_default_values(default_values)
		self.update_dependency_order()

	def load_schema(self):
		required = set()
		optional = set()
		ignored = set()
		unvalidated = set()
		definition_names = {}
		input_names = {}
		output_names = {}
		default_values = {}
		fields = {}
		if isinstance(self.schema.model, dict):
			fields = self.schema.model
		else:
			for entry in dir(self.schema.model):
				if entry.startswith('__'):
					continue
				field = getattr(self.schema.model, entry)
				if field is not None and isinstance(field, Field) is not True:
					continue
				fields[entry] = field
		for name in fields:
			field = fields[name]
			if field is None:
				field = Field(input_name=name)
			field_definition_name = name
			if field.definition_name is not None:
				field_definition_name = field.definition_name
			definition_names[name] = field_definition_name
			field_definition = Definitions.Index.get(field_definition_name)
			if field.required:
				required.add(name)
			else:
				optional.add(name)
			if field.ignored:
				ignored.add(name)
			if field.unvalidated:
				unvalidated.add(name)
			if field.output_name:
				output_names[name] = field.output_name
			if field.input_name:
				input_names[name] = field.input_name
			if not Utils.Empty.isempty(field.default_value):
				default_values[name] = field.default_value
			else:
				default_values[name] = field_definition.default_value
		self.add_spec(
				required=required,
				optional=optional,
				ignored=ignored,
				unvalidated=unvalidated,
				definition_names=definition_names,
				input_names=input_names,
				output_names=output_names,
				default_values=default_values
			)

	def get_field_definition_name(self, field_name):
		definition_name = field_name
		if field_name in self.definition_names:
			definition_name = self.definition_names[field_name]
		return definition_name

	def get_field_input_name(self, field_name):
		if field_name in self.input_field_names:
			return self.input_field_names[field_name]
		return field_name

	def get_field_input_display_name(self, field_name):
		if field_name in self.input_field_names:
			return self.input_field_display_names[field_name]
		return field_name

	def get_field_output_name(self, field_name):
		if field_name in self.output_names:
			return self.output_names[field_name]
		return field_name

	def _list_field_input_names(self, vector):
		result = []
		if isinstance(vector, dict):
			for k in vector:
				if self.schema.case_sensitive is False:
					k = k.lower()
				if k in self.input_value_names:
					result.append(self.input_value_names[k])
				else:
					result.append(k)
		else:
			for attribute_name in dir(vector):
				try:
					if attribute_name.startswith('_'):
						continue
					if not hasattr(vector, attribute_name): # possible dangling attr name if someone smashed the vector
						continue
					if callable(getattr(vector, attribute_name)):
						continue
					if self.schema.case_sensitive is False:
						attribute_name = attribute_name.lower()
					if attribute_name in self.input_value_names:
						result.append(self.input_value_names[attribute_name])
					else:
						result.append(attribute_name)
				except:
					pass
		return result

	def _get_input_value_name(self, fqn, field_name):
		value_name = field_name
		if value_name in self.input_field_names:
			value_name = self.input_field_names[field_name]
		return value_name

	def _get_input_value(self, fqn, field_name, source):
		value_name = self._get_input_value_name(fqn, field_name)
		if isinstance(source, dict):
			if value_name in source:
				return source[value_name]
		elif hasattr(source, value_name):
			return getattr(source, value_name)
		display_name = self.get_field_input_display_name(value_name)
		field_fqn = Config.definition_name_strategy.get_fqn(fqn, display_name)
		raise Config.exception_factory.create_input_error(field_fqn, 'Missing required value.')

	def _get_output_value(self, value_name, source):
		if isinstance(source, dict):
			return source[value_name]
		return getattr(source, value_name)

	def _set_output_value(self, field_name, target, value):
		value_name = field_name
		if field_name in self.input_field_names:
			value_name = self.input_field_names[field_name]
		if isinstance(target, dict):
			target[value_name] = value
		else:
			old_val = getattr(target, value_name)
			if old_val != value: # avoid overwriting read-only values
				setattr(target, value_name, value)
		return value

	def _resolve_field_definition(self, fqn, field_name, dependency_values, **kw):
		definition_name = self.get_field_definition_name(field_name)
		definition = Definitions.Index.get(definition_name)
		if definition.is_one_of():
			if self.schema.dependency_resolver is None:
				raise Config.exception_factory.create_input_error(fqn, 'Schema field dependency resolver missing.')
			try:
				definition_name = self.schema.dependency_resolver.resolve(fqn, field_name, dependency_values, **kw)
				if definition_name not in definition.get_data_format():
					msg = "Schema field cannot be '{0}' (must be one of: {1})".format(definition_name, definition.get_data_format())
					raise Config.exception_factory.create_internal_error(fqn, msg)
				definition = Definitions.Index.get(definition_name)
			except Exception as ex:
				raise Config.exception_factory.create_input_error(fqn, 'Schema field resolution failed: {0}.'.format(ex), exception=ex)
		return definition

	def _rename_output(self, src_field_name, target_field_name, target):
		if isinstance(target, dict):
			tmp = target[src_field_name]
			del target[src_field_name]
			target[target_field_name] = tmp
		else:
			tmp = getattr(target, src_field_name)
			delattr(target, src_field_name)
			setattr(target, target_field_name, tmp)

	def _iterate(self, validated, fqn, values, callback, **rules_kw):
		# Some objects could have dangling __dict__ entries (e.g. WebCore context)
		# and other objects shouldn't be smashed, so the original ref must be
		# returned.
		# SOLUTION: Overwrite defaults but always return the original
		#           ref where possible.
		result = Parameters.Index.ensure(validated)
		normalized = values
		if isinstance(values, dict):
			if self.schema.case_sensitive is False:
				values = {k.lower():values[k] for k in values}
			normalized = Parameters.Index(values)
		field_names = self._list_field_input_names(normalized)
		kw = Parameters.Index()
		missing = set(self.required)
		# Build kw
		##########
		if self.schema.load_defaults is True:
			for field_name in self.optional:
				if field_name in self.default_values:
					kw[field_name] = self.default_values[field_name]
		for field_name in field_names:
			if field_name in missing:
				missing.remove(field_name)
			elif field_name not in self.optional:
				if not self.schema.allow_unknown_fields:
					display_name = self.get_field_input_display_name(field_name)
					raise Config.exception_factory.create_input_error(Config.definition_name_strategy.get_fqn(fqn, display_name), 'Unknown field.')
				else:
					if self.schema.return_unknown_fields is True:
						result[field_name] = self._get_input_value(fqn, field_name, normalized)
					continue
			if field_name not in self.ignored:
				kw[field_name] = self._get_input_value(fqn, field_name, normalized)
		# Validate
		##########
		if len(missing) > 0:
			display_names = []
			for entry in missing:
				display_names.append(self.get_field_input_display_name(entry))
			raise Config.exception_factory.create_input_error(fqn, 'Missing required values: {0}'.format(', '.join(display_names)))
		for field_name in self.dependency_order:
			display_name = self.get_field_input_display_name(field_name)
			child_fqn = Config.definition_name_strategy.get_fqn(fqn, display_name)
			# Unvalidated
			#############
			if field_name in self.unvalidated:
				result[field_name] = self._get_input_value(fqn, field_name, normalized)
				continue
			# Default Value
			###############
			field_definition = self._resolve_field_definition(child_fqn, field_name, result, **rules_kw)
			if field_name not in kw:
				if field_definition.has_default_value() and field_name in self.required:
					result[field_name] = field_definition.get_default_value(field_name)
				continue
			# Normal Field
			##############
			definition_result = callback(
					validated=None,
					field_fqn=child_fqn,
					field_name=field_name,
					definition_or_name=field_definition,
					value=kw[field_name],
					version=field_definition.version,
					**rules_kw)
			for definition_result_entry in definition_result:
				self._set_output_value(
						definition_result_entry,
						result,
						self._get_output_value(
								definition_result_entry,
								definition_result
							)
					)
		# Output Names
		##############
		result_keys = self._list_field_input_names(result)
		for field_name in result_keys:
			input_value_name = self._get_input_value_name(fqn, field_name)
			if field_name in self.output_names:
				output_name = self.output_value_names[field_name]
				self._rename_output(input_value_name, output_name, result)
		return result

	def __call__(self, validated, fqn, field_name, definition, values, cb, **rules_kw):
		return self._iterate(
				validated,
				fqn,
				values,
				cb,
				**rules_kw
			)
