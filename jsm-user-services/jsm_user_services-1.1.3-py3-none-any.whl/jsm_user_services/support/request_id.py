from typing import Callable

from jsm_user_services.exception import RequestIDModuleNotFound
from jsm_user_services.support.import_utils import import_module_otherwise_none


def get_current_request_id_callable() -> Callable:
    django_request_id_module, flask_request_id_module = (
        import_module_otherwise_none("request_id_django_log.request_id"),
        import_module_otherwise_none("flask_log_request_id"),
    )

    if django_request_id_module is not None:
        return django_request_id_module.current_request_id

    if flask_request_id_module is not None:
        return flask_request_id_module.current_request_id

    raise RequestIDModuleNotFound


current_request_id = get_current_request_id_callable()
