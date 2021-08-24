from inspect import signature, iscoroutinefunction
from functools import wraps
from copy import deepcopy
from typing import Dict

def replace_arg_simple(new_arg_name: str, old_arg_name: str):
    """
    A much more simple version of replace arg.

    Replaces one arg name for another.
    Does not change function signatures.
    Compatible with functions containing *args or **kwargs.

    :param new_arg_name: The new name of the argument.
    :param old_arg_name: The old name of the argument.
    """
    def replace_arg_simple_inner(function):
        def inner(*args, **kwargs):
            if new_arg_name in kwargs:
                kwargs[old_arg_name] = kwargs.pop(new_arg_name)
            return function(*args, **kwargs)
        return inner
    return replace_arg_simple_inner

class MissingPositionals(TypeError):
    def __init__(self, function_name, args_list):
        def wordy_list(input_list):
            words = ''
            for counter, i in enumerate(input_list):
                if len(input_list) == 1:
                    words = str(i)
                elif counter == len(input_list) - 1:
                    words += 'and ' + str(i)
                elif counter == len(input_list) - 2:
                    words += str(i) + ' '
                else:
                    words += str(i) + ', '
            return words
        if len(args_list) == 1:
            argument_word = 'argument'
        else:
            argument_word = 'arguments'
        super().__init__(f'{function_name}() missing {len(args_list)} required positional {argument_word}: {wordy_list(args_list)}')

class TooManyPositionals(TypeError):
    def __init__(self, function_name, n_takes, n_supplied):
        if n_takes == 1:
            argument_word = 'argument'
        else:
            argument_word = 'arguments'
        if n_supplied == 1:
            plural = 'was'
        else:
            plural = 'were'
        super().__init__(f'{function_name}() takes {n_takes} positional {argument_word} but {n_supplied} {plural} given')

def replace_arg(parameter_to_replace: str, **new_args_to_replace: Dict[str, type]):
    """
    Replaces one argument in a function with multiple.

    :param parameter_to_replace: The name of the argument to be replaced.
    :param new_args_to_replace: All additional keyword arguments will be taken as follows:

    The key becomes the name of the argument replacing the parameter.
    The value is a dict detailing the configuration of the replacement.

    Acceptable values in the dict are:

    'annotation': The type annotation of the new field. (optional)
    'default': The default value of the argument. (optional)
    'kind': The kind of the parameter. (Note: Experimental, change at your own risk) (optional)
    
    e.g. test = {'annotation': str}

    Incompatible with functions containing *args or **kwargs
    """
    def replace_arg_inner(f):
        def replace_signature(source, destination, parameters):
            destination.__signature__ = signature(source).replace(parameters=parameters)
            return destination
        def make_new_parameters(source, new_args_to_replace):
            original_parameters = list(signature(source).parameters.values())
            parameter_index = [x.name for x in original_parameters].index(parameter_to_replace)
            relevant_parameter = original_parameters.pop(parameter_index)
            additional_arg_params_list = []
            additional_kwarg_params_list = []
            for arg_name, details in new_args_to_replace.items():
                new_details = deepcopy(details)
                new_details['name'] = arg_name
                new_parameter = relevant_parameter.replace(**new_details)
                if new_parameter.default == new_parameter.empty:
                    additional_arg_params_list.append(new_parameter)
                else:
                    additional_kwarg_params_list.append(new_parameter)
            original_arg_parameters = [x for x in original_parameters if x.default == x.empty]
            original_kwarg_parameters = [x for x in original_parameters if not(x.default == x.empty)]
            full_parameters = original_arg_parameters + additional_arg_params_list + original_kwarg_parameters + additional_kwarg_params_list
            return original_parameters, full_parameters

        def map_args_to_kwargs(function_name, args, kwargs, full_parameters):
            def check_args_within_bounds(n_args_supplied, n_pos, new_parameter_names_list, kwargs):      
                if n_pos > n_args_supplied:
                    relevant_args = [i for i in new_parameter_names_list[n_args_supplied: n_pos] if i not in kwargs]
                    if len(relevant_args) > 0:
                        raise MissingPositionals(function_name, relevant_args)
                if n_args_supplied > len(new_parameter_names_list):
                    raise TooManyPositionals(function_name, len(new_parameter_names_list), n_args_supplied)
            
            args_list = list(args)
            n_args_supplied = len(args_list)
            parameter_names_list = [param.name for param in full_parameters]
            
            check_args_within_bounds(
                n_args_supplied, 
                len([i for i in full_parameters if i.default == i.empty]), 
                parameter_names_list, 
                kwargs
            )
            for counter in range(n_args_supplied):
                new_sig_name = parameter_names_list[counter]
                if new_sig_name in kwargs:
                    raise TypeError(f'{function_name}() got multiple values for argument \'{new_sig_name}\'')
                kwargs[new_sig_name] = args_list[counter]
            return kwargs
        
        def make_fresh_kwargs(kwargs, original_parameters, new_parameters, new_args_to_replace):
            new_form_kwargs = {param.name: param.default for param in new_parameters}
            new_form_kwargs.update(kwargs)
            additional_params = [x for x in new_args_to_replace]
            output_kwargs = {}
            additional_params_dict = {}
            for arg_name, value in new_form_kwargs.items():
                if arg_name in additional_params:
                    additional_params_dict[arg_name] = value
                    output_kwargs[parameter_to_replace] = additional_params_dict
                elif arg_name == parameter_to_replace:
                    raise TypeError(f'{f.__name__}() got an unexpected keyword argument \'{arg_name}\'')
                else:
                    output_kwargs[arg_name] = value
            return output_kwargs
        
        original_parameters, new_parameters = make_new_parameters(f, new_args_to_replace)

        if iscoroutinefunction(f):
            @wraps(f)
            async def inner(*args, **kwargs):
                kwargs = map_args_to_kwargs(f.__name__, args, kwargs, new_parameters)
                fresh_kwargs = make_fresh_kwargs(kwargs, original_parameters, new_parameters, new_args_to_replace)
                return await f(**fresh_kwargs)
        else:
            @wraps(f)
            def inner(*args, **kwargs):
                kwargs = map_args_to_kwargs(f.__name__, args, kwargs, new_parameters)
                fresh_kwargs = make_fresh_kwargs(kwargs, original_parameters, new_parameters, new_args_to_replace)
                return f(**fresh_kwargs)
        
        return replace_signature(f, inner, new_parameters)
    return replace_arg_inner

def replace_args(**new_args_to_replace: Dict[str, type]):
    """
    Replaces multiple arguments in a function with multiple.

    :param new_args_to_replace: All keyword arguments will be taken as follows:

    The key becomes the name of the argument replacing the parameter.
    The value is a dict detailing the configuration of the replacement.

    Acceptable values in the dict are:
    'replaces': The field to replace (required)
    'annotation': The type annotation of the new field. (optional)
    'default': The default value of the argument. (optional)
    'kind': The kind of the parameter. (Note: Experimental, change at your own risk) (optional)
    
    e.g. test = {'replaces': 'test2', 'annotation': str}

    Incompatible with functions containing *args or **kwargs
    """
    def replace_args_inner(f):
        function_groups = {}
        for arg_name, details in new_args_to_replace.items():
            if isinstance(details, str):
                details = {'replaces': details}
            try:
                arg_to_replace = details.pop('replaces')
            except KeyError:
                raise ValueError(f'\'replaces\' missing for {arg_name}')
            if arg_to_replace in function_groups:
                function_groups[arg_to_replace][arg_name] = details
            else:
                function_groups[arg_to_replace] = {arg_name: details}
        
        function_wrapped = f
        for arg_name, function_group in function_groups.items():
            function_wrapped = replace_arg(arg_name, **function_group)(function_wrapped)
        return function_wrapped
    return replace_args_inner
