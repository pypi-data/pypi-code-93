import cro_validate.api.configuration_api as ConfigApi


def create_input_error(source, message, internal_message=None, exception=None, **kw):
	return ConfigApi.get_exception_factory().create_input_error(source, message, internal_message, exception, **kw)
		

def create_internal_error(source, message, exception=None, **kw):
	return ConfigApi.get_exception_factory().create_internal_error(source, message, exception, **kw)