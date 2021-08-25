from copy import deepcopy
from enum import Enum
from functools import lru_cache
import importlib.util
import json
from logging import getLogger
from inspect import Parameter, Signature
from pathlib import Path, PurePosixPath
import shutil
import sys
import warnings

from docstring_parser import parse as parse_docstring
import yaml
from roboversion import get_version

from phantom_dev.dummy import MockedPhantomModule
with MockedPhantomModule():
	from phantom_dev import action_handler

from .requirements import download_requirements


logger = getLogger(name=__name__)


class InferrableField:
	def __init__(self, inference_method, json_path=None):
		self.name = None
		self.inference_method = inference_method
		self.json_path = json_path

	def __set_name__(self, owner, name):
		self.name = name

	def __get__(self, obj, owner=None):
		if obj is None:
			return self

		try:
			return obj.metadata[self.name]
		except KeyError:
			logger.debug(
				'Attempting to infer value for metadata key %r', self.name)
			value = self.inference_method(obj)
			logger.info('Inferred value for %r: %r', self.name, value)
			return value

	def __set__(self, obj, value):
		obj.metadata[self.name] = value


class App:
	ANNOTATION_MAP = {
		bool: 'boolean',  # Check bool before int as bool is an int subclass
		str: 'string',
		int: 'numeric',
		float: 'numeric',
	}

	REQUIRED_ACTION_KEYS = {
		'name',
		'description',
		'parameters',
	}

	REQUIRED_PARAMETER_KEYS = [
		'description',
		'data_type',
	]

	DEFAULT_APP_TYPE = 'prototype'
	DEFAULT_ACTION_TYPE = 'prototype'

	DEFAULT_LOGO_PATH = Path(__file__).absolute().parent.joinpath(
		'default_logo.svg')

	def __init__(self, path):
		self.path = Path(path).absolute()
		logger.debug('Initialising app with path %r', self.path)
		self._raw_json = None

	@property
	@lru_cache()
	def metadata(self):
		return self._load_metadata()

	@property
	def id(self):
		return self.metadata['id']

	@InferrableField
	def name(self):
		return self.path.name

	@InferrableField
	def main_module(self):
		module_path = self.path.joinpath('connector.py')
		if module_path.exists():
			return module_path.name

		raise FileNotFoundError(module_path)

	@InferrableField
	def package_name(self):
		compact_name = self.name.lower()
		for separator in [None, '_']:  # Default splitting and on underscore
			name_tokens = compact_name.split(sep=separator)
			compact_name = ''.join(name_tokens)

		return compact_name

	@InferrableField
	def type(self):
		logger.warning('No app type specified')
		return self.DEFAULT_APP_TYPE

	def get_version(self, *args, **kwargs):
		try:
			return self.metadata['version']
		except KeyError:
			pass

		try:
			version = get_version(*args, project_path=self.path, **kwargs)
		except Exception as error:
			logger.exception(error)
			version = '0.0.0'
			logger.warning(
				(
					'Unable to infer app version from project git repository;'
					' using default version %r.'
				),
				version,
			)
			logger.warning(
				(
					' Configure the repository (recommended) or specify'
					' "version" in metadata (not recommended)'
				),
			)
			return version

		return str(version)

	def get_connector(self):
		connector_path = self.path.joinpath(self.main_module)
		module_name = f'{connector_path.stem}_{self.id}'
		try:
			module = sys.modules[module_name]
		except KeyError:
			spec = importlib.util.spec_from_file_location(
				name=module_name, location=connector_path)
			
			module = importlib.util.module_from_spec(spec)
			module.__path__ = connector_path
			with MockedPhantomModule():
				spec.loader.exec_module(module)
				sys.modules[module_name] = module

		registered_connectors = action_handler.registered_connectors
		try:
			all_connectors = registered_connectors[module.__name__]
		except KeyError:
			logger.error(
				'module %r not found in registered connectors map %r',
				module,
				action_handler.registered_connectors,
			)

			raise

		try:
			connector_class, = all_connectors
		except ValueError:
			logger.error('Too many connectors')
			for connector in all_connectors:
				logger.error(
					'%r from module %r', connector, connector.__module__)
			raise

		return connector_class

	def get_logo_json(self):
		try:
			data = self.metadata['logo']
		except KeyError:
			try:
				logo_light_path, = self.path.glob('logo_light.*')
			except ValueError:
				try:
					logo_path, = self.path.glob('logo.*')
				except ValueError:
					logo_path = self.path.joinpath(
						f'logo{self.DEFAULT_LOGO_PATH.suffix}')

					shutil.copy2(self.DEFAULT_LOGO_PATH, logo_path)

				logo = logo_path.name
				return {'logo': logo}

			logo_light = logo_light_path.name
			logo_dark_path, = self.path.glob('logo_dark.*')
			logo_dark = logo_dark_path.name
			return {'logo': logo_light, 'logo_dark': logo_dark}

		if isinstance(data, str):
			return {'logo': data}

		result = {'logo': data['light']}
		if 'dark' in data:
			result['dark'] = data['dark']

		return result

	def get_configuration_json(self):
		data = self.metadata.get('configuration', {})
		output = {}
		for index, (name, item) in enumerate(data.items()):
			output[name] = item.copy()
			output[name]['order'] = index

		return output

	def get_pip_json(self):
		pip_data = self.metadata.get('pip_dependencies', {})

		data = {}
		try:
			pypi_data = pip_data['pypi']
		except KeyError:
			logger.debug('No PyPI data')
		else:
			data['pypi'] = [{'module': x} for x in pypi_data]

		try:
			wheel_data = pip_data['wheels']
		except KeyError:
			logger.debug('No wheels data')
		else:
			data['wheel'] = [
				{'module': x, 'input_file': f'wheels/{y}'}
				for x, y in wheel_data.items()
			]
		
		return data

	def get_json_action_items(self):
		specified = self.metadata.get('actions', {})
		logger.debug('Specified action metadata: %r', specified)
		try:
			connector_class = self.get_connector()
		except (KeyError, ValueError) as error:
			logger.exception(error)
			warnings.warn(
				'No phantom-dev connector class found;'
				' unable to infer metadata from handler code'
			)
			merged_metadata = specified
		else:
			inferred = {}
			for handler in connector_class.get_handlers():
				identifier = handler.action_identifier
				inferred[identifier] = self._infer_action_metadata(handler)

			merged_metadata = self._merge_inferences(specified, inferred)

		for identifier, action_data in merged_metadata.items():
			action_data.setdefault('versions', 'EQ(*)')
			if 'type' not in action_data:
				logger.warning(
					f'Missing type for action {identifier!r};'
					f' setting type to {self.DEFAULT_ACTION_TYPE!r}'
				)
				action_data['type'] = self.DEFAULT_ACTION_TYPE

			missing_keys = [
				k for k in self.REQUIRED_ACTION_KEYS if k not in action_data]
			if missing_keys:
				message = (
					f'Action {identifier !r} is missing values for required'
					f' keys {missing_keys!r}.'
				)
				if 'description' in missing_keys:
					message += (
						' A description can be added by setting a handler'
						' method docstring.'
					)

				raise KeyError(message)

			action_parameters = action_data.get('parameters', {})

			# Automate parameter ordering unless a value for 'order' has been
			# specified for any of the parameters
			automate_parameter_ordering = True

			for name, data in action_parameters.items():
				if 'order' in data:
					automate_parameter_ordering = False

				missing_keys = [
					k for k in self.REQUIRED_PARAMETER_KEYS if k not in data]
				if missing_keys:
					raise KeyError(
						f'Action {identifier !r} parameter {name!r} is'
						f' missing values for required keys {missing_keys!r}'
					)

				output_data = action_data.setdefault('output', {})
				datapath = f'action_result.parameter.{name}'
				parameter_output = output_data.setdefault(datapath, {})
				parameter_output.setdefault('data_type', data['data_type'])
				try:
					contains = data['contains']
				except KeyError:
					logger.warning(
						f'Action {identifier !r} parameter {name!r} lacks'
						' contains data'
					)
				else:
					parameter_output.setdefault('contains', contains)

			if automate_parameter_ordering:
				for order, data in enumerate(action_parameters.values()):
					data['order'] = order

			# Convert name key to action key
			action_data['action'] = action_data.pop('name')
			# Convert output dict to list
			output = action_data.pop('output', {})
			new_output = []
			for data_path, output_data in output.items():
				output_item = {**output_data, 'data_path': data_path}
				new_output.append(output_item)

			action_data['output'] = new_output

			# Actions is a list instead of a dict
			yield {'identifier': identifier, **action_data}

	def get_json(self):
		json_data = {
			'appid': self.id,
			'name': self.name,
			'description': self.metadata['description'],
			'type': self.type,
			'main_module': self.main_module,
			'app_version': self.get_version(),
			'pip_dependencies': self.get_pip_json(),
			'min_phantom_version': self.metadata.get(
				'min_phantom_version', '4.8.0'),
			'product_vendor': self.metadata['product']['vendor'],
			'product_name': self.metadata['product']['name'],
			'product_version_regex': self.metadata['product'].get(
				'version_regex', '.*'),
			'publisher': self.metadata['publisher'],
			'package_name': f'phantom_{self.package_name}',
			'license': self.metadata['license'],
			'configuration': self.get_configuration_json(),
			**self.get_logo_json(),
			'actions': list(self.get_json_action_items()),
			'python_version': self.metadata.get('python_version', '3'),
		}

		if json_data['python_version'] != '3':
			logger.warning('App is not implemented for Python 3')

		for optional_key in ['url', 'consolidate_widgets']:
			try:
				json_data[optional_key] = self.metadata[optional_key]
			except KeyError:
				pass

		return json_data

	def build(self, directory: Path):
		package_name = f'ph{self.package_name}'
		package_path = directory.joinpath(package_name)
		if package_path.exists():
			shutil.rmtree(package_path)

		copy_tree(self.path, package_path)
		if self._raw_json is not None:
			logger.warning('JSON metadata prevents advanced build features')
			return package_path

		module_path_string, = action_handler.__path__
		module_path = Path(module_path_string)
		top_package_path = module_path.parent
		relative_path = module_path.relative_to(top_package_path)
		dependency_path = package_path.joinpath(
			'dependencies', top_package_path.name, relative_path)

		dependency_path.parent.mkdir(exist_ok=True, parents=True)
		copy_tree(module_path, dependency_path)

		app_json = self.get_json()

		requirement_files = {
			x: package_path.joinpath(f'requirements-{x}.txt')
			for x in ['whl', 'sdist', 'pypi']
		}

		if not requirement_files['whl'].exists():
			deprecated_requirements = package_path.joinpath('requirements.txt')
			if deprecated_requirements.exists():
				logger.warning(
					f'{deprecated_requirements} is deprecated and will break'
					f' soon; use {requirement_files["whl"]} for wheel'
					' requirements'
				)
				requirement_files['whl'] = deprecated_requirements

		if any(requirement_files[k].exists() for k in ['whl', 'sdist']):
			wheels = package_path.joinpath('wheels')
			wheels.mkdir(exist_ok=True)
			for name, package in download_requirements(
					wheels,
					requirement_files['whl'],
					requirement_files['sdist'],
			):
				posix_path = PurePosixPath(package.relative_to(package_path))
				data = {
					'module': name,
					'input_file': str(posix_path),
				}
				wheels_data = app_json['pip_dependencies'].setdefault(
					'wheel', [])

				wheels_data.append(data)

		if requirement_files['pypi'].exists():
			with requirement_files['pypi'].open() as pypi_file:
				for requirement in pypi_file.readlines():
					data = {'module': requirement.strip()}
					packages_data = app_json['pip_dependencies'].setdefault(
						'pypi', [])
					packages_data.append(data)

		json_path = package_path.joinpath(f'autogenerated.json')
		with json_path.open('w') as json_file:
			json.dump(app_json, json_file, indent='\t')

		logger.debug('Wrote app JSON to %r', json_path)

		return package_path

	def _load_metadata(self):
		try:
			metadata_path = self._find_json()
		except FileNotFoundError:
			logger.debug('No JSON metadata; can continue with YAML metadata')
		else:
			logger.warning('YAML metadata should be used instead of JSON')
			with metadata_path.open() as json_file:
				self._raw_json = json.load(json_file)

			return self._normalise_json_metadata(self._raw_json)

		metadata_path = self.path.joinpath('metadata.yaml')
		with metadata_path.open() as metadata_file:
			return yaml.safe_load(metadata_file)

	def _find_json(self):
		json_candidates = list(self.path.glob('*.json'))
		try:
			metadata_path, = json_candidates
		except ValueError as error:
			if not json_candidates:
				raise FileNotFoundError('No metadata JSON found')

			message = (
				'Multiple JSON metadata candidates detected:'
				f' {json_candidates}'
			)
			raise ValueError(message) from error

		return metadata_path

	@classmethod
	def _get_data_type(cls, type_obj):
		logger.debug('Getting data_type for %r', type_obj)
		if issubclass(type_obj, Enum):
			value_types = [type(e.value) for e in type_obj]
			enum_data_types = set(cls._get_data_type(t) for t in value_types)
			try:
				data_type, = enum_data_types
			except ValueError as error:
				message = (
					f'Unable to infer data_type from {Enum} subclass'
					f' {type_obj} with value types {value_types};'
					f' Exactly one data_type must be inferrable, candidates'
					f' are: {enum_data_types}'
				)
				raise TypeError(message) from error

			return data_type

		for base_type, data_type in cls.ANNOTATION_MAP.items():
			if issubclass(type_obj, base_type):
				return data_type

		raise KeyError(f'{type_obj} not in {cls.ANNOTATION_MAP}')

	def _infer_action_metadata(self, handler: action_handler.ActionHandler):
		metadata = {}
		handler_method = handler.handler_method
		name_tokens = handler_method.__name__.split('_')
		metadata['name'] = ' '.join(name_tokens)
		metadata['read_only'] = handler.read_only
		if handler.action_type is not None:
			metadata['type'] = handler.action_type

		docstring = handler_method.__doc__
		if docstring is None:
			method_doc = None
			parameter_descriptions = {}
		else:
			method_doc = parse_docstring(docstring)
			metadata['description'] = method_doc.short_description
			if method_doc.long_description is not None:
				metadata['verbose'] = method_doc.long_description

			parameter_descriptions = {
				p.arg_name: p.description for p in method_doc.params}

		if handler.data_contains_map is not None:
			output_data = metadata.setdefault('output', {})
			for key, type_obj in handler.data_contains_map.items():
				output_data[f'action_result.data.*.{key}'] = {
					'contains': action_handler.contains_map[type_obj],
					'data_type': self._get_data_type(type_obj)
				}

		if handler.summary_contains_map is not None:
			output_data = metadata.setdefault('output', {})
			for key, type_obj in handler.summary_contains_map.items():
				try:
					contains = action_handler.contains_map[type_obj]
				except KeyError:
					logger.debug(
						'Summary type %r has no contains', type_obj)

					contains = []

				output_data[f'action_result.summary.{key}'] = {
					'contains': contains,
					'data_type': self._get_data_type(type_obj)
				}

		if handler.custom_view_metadata is not None:
			metadata['render'] = dict(handler.custom_view_metadata)
			view_function = handler.custom_view_function
			view_module = sys.modules[view_function.__module__]
			view_module_path = Path(view_module.__path__)
			try:
				view_module, = view_module_path.relative_to(self.path).parts
			except ValueError as error:
				raise ValueError(
					f'View function module {view_module_path} is not located'
					' in the top-level app directory'
				) from error

			view_entry = f'{view_module_path.stem}.{view_function.__name__}'
			metadata['render']['view'] = view_entry

		if handler.lock is None:
			metadata['lock'] = {'enabled': False}
		elif handler.lock is handler.DEFAULT_LOCK:
			metadata['lock'] = {'enabled': True}
		else:
			metadata['lock'] = {'enabled': True, 'data_path': handler.lock}

		if handler.lock_timeout is not None:
			metadata['lock']['timeout'] = handler.lock_timeout

		signature = Signature.from_callable(handler_method)
		for name, parameter in signature.parameters.items():
			parameters_data = metadata.setdefault('parameters', {})
			if name in ['self', 'context']:
				continue

			if parameter.kind in [
					parameter.VAR_POSITIONAL, parameter.VAR_KEYWORD]:
				continue

			inferred_data = self._infer_parameter_metadata(parameter)
			parameters_data[name] = inferred_data
			try:
				inferred_data['description'] = parameter_descriptions[name]
			except KeyError:
				logger.debug(
					'Action %r parameter %r lacks a description',
					metadata['name'],
					name,
				)

		return metadata

	@classmethod
	def _infer_parameter_metadata(cls, parameter: Parameter):
		if parameter.default is parameter.empty:
			metadata = {'required': True}
		else:
			metadata = {'required': False, 'default': parameter.default}

		annotation = parameter.annotation
		if annotation is parameter.empty:
			return metadata

		metadata['data_type'] = cls._get_data_type(annotation)

		try:
			contains = action_handler.contains_map[annotation]
		except KeyError:
			logger.error(
				f'Unable to infer parameter {parameter.name!r} contains data'
				f' from annotation {annotation!r}'
			)
		else:
			metadata['contains'] = contains

		if issubclass(annotation, Enum):
			metadata['value_list'] = [e.value for e in annotation]

		return metadata

	@staticmethod
	def _normalise_json_metadata(metadata):
		logger.debug('Normalising metadata: %r', metadata)
		normalised = dict(metadata)
		normalised['id'] = normalised.pop('appid')
		normalised['version'] = normalised.pop('app_version')
		normalised['package_name'] = normalised['package_name'].lstrip(
			'phantom_')

		# Pack product config
		product = normalised.setdefault('product', {})
		product['name'] = normalised.pop('product_name')
		product['vendor'] = normalised.pop('product_vendor')
		product['version_regex'] = normalised.pop('product_version_regex')

		# Pack logo config
		logo = {}
		logo['light'] = normalised.pop('logo')
		try:
			logo['dark'] = normalised.pop('logo_dark')
		except KeyError:
			pass
		
		normalised['logo'] = logo

		# Define config items in in specified order
		configuration = normalised.pop('configuration')
		max_order = max(v.get('order', -1) for v in configuration.values())
		for key, value in sorted(
				configuration.items(),
				key=lambda t: t[1].get('order', max_order + 1)
		):
			normalised.setdefault('configuration', {})[key] = value

		# Pip data
		pip_data = normalised.get('pip_dependencies', {})
		try:
			pypi_data = pip_data.pop('pypi')
		except KeyError:
			pass
		else:
			pip_data['pypi'] = [i['module'] for i in pypi_data]

		try:
			wheel_data = pip_data.pop('wheel')
		except KeyError:
			pass
		else:
			pip_data['wheels'] = {
				i['module']: i['input_file'].lstrip('wheels/')
				for i in wheel_data
			}

		if pip_data:
			normalised['pip_dependencies'] = pip_data

		# Translate action config
		actions = {}
		for action_data in normalised.pop('actions', []):
			identifier = action_data.pop('identifier')
			actions[identifier] = action_data
			# Rename 'action' to 'name'
			action_data['name'] = action_data.pop('action')
			# Convert output list to dict
			for output in action_data.pop('output', []):
				datapath = output.pop('data_path')
				action_data.setdefault('output', {})[datapath] = output

		normalised['actions'] = actions

		return normalised

	@classmethod
	def _merge_inferences(cls, metadata, inferences):
		result = deepcopy(metadata)
		for key, value in inferences.items():
			if isinstance(metadata.get(key), dict):
				result[key] = cls._merge_inferences(metadata[key], value)
				continue

			result.setdefault(key, value)

		return result


def copy_tree(source: Path, destination: Path):
	shutil.copytree(source, destination, ignore=lambda x, y: ['__pycache__'])
