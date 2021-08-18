from cro_validate.classes.configuration_classes import Config


class Index(dict):
	def __getattr__(self, name):
		resolved = Config.parameter_name_resolver.resolve(self, name)
		if resolved is None:
			#raise Config.exception_factory.create_input_error(name, 'Unresolved name.')
			#raise Config.exception_factory.create_internal_error(name, 'Unresolved name.')
			raise AttributeError() # to comply with hasattr
		result = self[resolved]
		return result

	def __setattr__(self, name, value):
		self[name] = value

	def ensure(index):
		if index is None:
			return Index()
		if isinstance(index, dict):
			return index
		raise Config.exception_factory.create_input_error(
				'ParameterIndex',
				'Invalid index input type {0}.'.format(type(index))
			)