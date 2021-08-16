from typing import List

from aide_sdk.messaging.pacs_client import AbstractPacsClient
from aide_sdk.model.origin import Origin
from aide_sdk.model.resource import Resource
from aide_sdk.manifests.execution_context import ExecutionContext


class OperatorContext:
    """
    This class is provided to Operators in their .process() method.
    It is this class which allows access to the AIDE context in which this operator is executed.
    It allows retrieving available resources and adding new resources.
    """
    def __init__(self,
                 origin: Origin,
                 resources: List[Resource],
                 execution_context: ExecutionContext,
                 correlation_uid: str,
                 pacs_client: AbstractPacsClient):
        self._origin = origin
        self._resources = resources
        self._execution_context = execution_context
        self._correlation_id = correlation_uid
        self._added_resources = list()
        self._failure = False
        self._failure_message = None
        self._error = False
        self._error_message = None
        self._pacs_client = pacs_client

    def add_resource(self, resource: Resource):
        if not isinstance(resource, Resource):
            raise ValueError("Tried to add bad resource")
        resource.namespace = self._execution_context.model_uid
        self._added_resources.append(resource)

    def set_failure(self, failure: str):
        self._failure = True
        self._failure_message = failure

    def set_error(self, error: str):
        self._error = True
        self._error_message = error

    @property
    def resources(self):
        return self._resources + self._added_resources

    def get_resources_by_type(self, format: str, content_type: str):
        return (x for x in self.resources
                if x.format == format and x.content_type == content_type)

    @property
    def origin(self):
        return self._origin
