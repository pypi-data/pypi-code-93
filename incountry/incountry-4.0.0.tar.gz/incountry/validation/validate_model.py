from typing import Dict, Union

import wrapt
from pydantic import BaseModel, ValidationError


from .utils import function_args_to_kwargs, get_formatted_validation_error
from ..exceptions import StorageException, StorageClientException, StorageServerException


def path_to_obj(root_obj, attr_path):
    obj = root_obj
    for attr in attr_path:
        obj = getattr(obj, attr)
    return obj


def get_res_model(model, class_instance):
    res_model = model
    if isinstance(model, dict) and isinstance(class_instance, object):
        condition_value = path_to_obj(class_instance, model["condition"])
        for option in model["values"]:
            if condition_value == option["value"]:
                res_model = option["model"]

    return res_model


def get_validated_data(function, model, exclude_to_dict, **kwargs):
    try:
        return model.validate(kwargs).dict(exclude=exclude_to_dict, exclude_unset=True)
    except ValidationError as e:
        errors_report = get_formatted_validation_error(e)
        error_text = "Validation failed during {}():{}".format(function.__qualname__, errors_report)
        raise StorageClientException(error_text) from None


def validate_model(model: Union[BaseModel, Dict], exclude_to_dict={}):
    @wrapt.decorator
    def decorator(function, instance, args, kwargs):
        new_kwargs = dict(kwargs)
        res_model = get_res_model(model, instance)

        function_args_to_kwargs(function, args, new_kwargs)

        validated_data_dict = get_validated_data(function, res_model, exclude_to_dict, **new_kwargs)

        exception_context_str = f"during {function.__qualname__}()"

        for key in new_kwargs:
            if key in validated_data_dict:
                new_kwargs[key] = validated_data_dict[key]
        try:
            return function(**new_kwargs)
        except StorageClientException as e:
            if exception_context_str in str(e):
                raise e
            raise StorageClientException(f"Validation failed {exception_context_str}") from e
        except StorageServerException as e:
            if exception_context_str in str(e):
                raise e
            raise StorageServerException(f"Server exception {exception_context_str}") from e
        except StorageException as e:
            raise e
        except Exception as e:
            raise StorageException(f"{e.__class__.__qualname__} {exception_context_str}") from e

    return decorator
