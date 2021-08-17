from typing import Union, Callable, Dict

from skill_core_tools.skill_log_factory import SkillLogFactory
import logging

logger = SkillLogFactory.get_logger("Endpoints")


class Endpoints:
    """
    Stores handler methods for different namespaces and executes the correct
    handler based on the namespace provided in the request context.
    """

    def __init__(self, log_level: int = logging.DEBUG) -> None:
        """

        :param log_level: integer to specify
        """
        if not isinstance(log_level, int):
            raise TypeError("log_level must be an integer. Use the logging package e.g. logging.DEBUG")
        self._log_level = log_level
        self._endpoints: Dict[str, Callable[[dict, dict], dict]] = {}

    def add(self, namespace: str, handler: Callable[[dict, dict], dict]) -> None:
        """
        Stores a handler for a given namespace.

        :param namespace: a namespace identifier.
        :param handler: a handler function that takes a payload dict & a context dict as input.
        :return:
        :raise ValueError if the provided namespace is undefined/blank or if the namespace has already been defined.
        """
        if namespace is None or namespace.strip() == "":
            raise ValueError("Endpoints can only be added for non-blank namespaces.")
        if namespace in self._endpoints:
            raise ValueError("Endpoint for namespace %s has already been defined.", namespace)
        self._endpoints[namespace] = handler
        logger.log(self._log_level, "Endpoint added: %s", namespace)

    def handle(self, payload: dict, context: dict) -> dict:
        """
        Handles a request by calling the endpoint associated with the namespace in the context.

        :param payload: payload of a request
        :param context: context of a request
        :return: response of the endpoint enriched by namespace information
        :raise ValueError if no endpoint is associated with the namespace in the context.
        """
        relevant_namespace = _get_relevant_namespace(context)
        without_grave_accents = _remove_grave_accents(relevant_namespace)

        logger.log(self._log_level, "Handling request to endpoint: %s", relevant_namespace)
        logger.log(self._log_level, "Request payload: %s", payload)

        if without_grave_accents not in self._endpoints:
            raise ValueError("No endpoint was defined for provided namespace '{}'".format(relevant_namespace))
        response = self._endpoints[without_grave_accents](payload, context)

        logger.log(self._log_level, "Request to endpoint complete: %s".format(relevant_namespace))
        logger.log(self._log_level, "Response payload: %s", response)

        return attach_namespace(relevant_namespace, response)


def attach_namespace(namespace_or_context: Union[str, dict], response_map: dict) -> dict:
    """
    Attaches the given namespace to the response map

    Example:
        >>> attach_namespace('echo', {'response' : 'hello world'})
        {'@echo': {'response': 'hello world'}}
        >>> attach_namespace({'namespace' : 'echo.incoming'}, {'response' : 'hello world'})
        {'@echo': {'response': 'hello world'}}

    :param namespace_or_context: either a string specifying the namespace or the evaluation context
    :param response_map:
    :return:
    """
    if type(namespace_or_context) == str:
        return {'@{}'.format(namespace_or_context): response_map}
    if type(namespace_or_context) == dict:
        extracted_ns = namespace_or_context.get("namespace")

        if extracted_ns is None:
            _raise_on_missing_namespace(namespace_or_context)

        parent_ns = extracted_ns.split('.')[0]
        return attach_namespace(parent_ns, response_map)
    raise TypeError('Can not extract namespace from the given type {}'.format(type(namespace_or_context)))


def is_namespace(context: dict, namespace: str):
    """
    Checks if the current context is in the given namespace.
    :raises Exception if an invalid context is passed

    Example:
        >>> is_namespace({'namespace': 'test.incoming'}, 'test')
        True
        >>> is_namespace({'namespace': '`test`.incoming'}, 'test')
        True

    :param context:
    :param namespace:
    :return:
    """
    relevant_namespace = _get_relevant_namespace(context)
    return _remove_grave_accents(namespace) == _remove_grave_accents(relevant_namespace)


def _remove_grave_accents(namespace: str) -> str:
    """
    Removes the grave accents if present
    :param namespace:
    :return:
    """
    return namespace.replace("`", "")


def _get_relevant_namespace(context: dict) -> str:
    _check_context(context)
    ns = context.get("namespace")
    if ns is None:
        _raise_on_missing_namespace(context)
    return _extract_relevant(ns)


def _extract_relevant(namespace: str) -> str:
    """
    Extracts the relevant part of a full namespace
    Given the namespace 'test.incoming' => 'test'
    :param namespace:
    :return:
    """
    if namespace is None:
        raise TypeError('None is not a valid namespace')
    split_without_last = namespace.split(".")[:-1]
    return ".".join(split_without_last)


# side effects:
def _raise_on_missing_namespace(corrupted_context):
    raise Exception(
        'The passed context does not contain a namespace - did you really pass the evaluation context?\ncontext={}'.format(
            corrupted_context))


def _check_context(context):
    if type(context) != dict:
        raise TypeError("'{}' is not an evaluation context!".format(context))
