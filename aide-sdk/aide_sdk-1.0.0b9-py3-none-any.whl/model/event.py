import copy
import dataclasses
import datetime
from json import JSONDecodeError
from typing import List

import marshmallow.exceptions

from aide_sdk.logger.logger import LogManager
from aide_sdk.messaging.pacs_client import AbstractPacsClient
from aide_sdk.model.operatorcontext import OperatorContext
from aide_sdk.model.origin import Origin
from aide_sdk.model.resource import Resource
from aide_sdk.messaging.schemas.event import EventSchema
from aide_sdk.manifests.execution_context import ExecutionContext
from aide_sdk.messaging.schemas.event_execution import EventExecutionSchema


@dataclasses.dataclass
class Event:
    correlation_id: str
    origin: Origin
    resources: List[Resource]
    executions: List[ExecutionContext]
    _execution_context: ExecutionContext = dataclasses.field(default=None, init=False)
    _operator_context: OperatorContext = dataclasses.field(default=None, init=False)
    start_time: datetime.datetime = dataclasses.field(default=datetime.datetime.utcnow(), init=False)
    end_time: datetime.datetime = dataclasses.field(default=None, init=False)

    def add_resources(self, resources):
        self.resources.extend(resources)

    def add_execution(self, execution_context: ExecutionContext):
        self.executions.append(execution_context)

    def process_result_context(self, context: OperatorContext):
        self._operator_context = context
        self.resources.extend(context._added_resources)

    def get_operator_context(self, pacs_client: AbstractPacsClient):
        if not self._operator_context:
            event_resources = [copy.deepcopy(x) for x in self.resources]
            origin = copy.deepcopy(self.origin)
            self._operator_context = OperatorContext(origin,
                                                     event_resources,
                                                     self._execution_context,
                                                     self.correlation_id,
                                                     pacs_client)
        return self._operator_context

    def to_message(self):
        try:
            LogManager._get_audit_logger().debug("Serialising event")
            schema = EventSchema()
            message = schema.dumps(self)
            return message
        except Exception:
            LogManager._get_audit_logger().error("Could not serialise event")
            raise

    def to_execution(self):
        try:
            LogManager._get_audit_logger().debug("Serialising event to elastic execution")
            schema = EventExecutionSchema()
            message = schema.dumps(self)
            return message
        except Exception:
            LogManager._get_audit_logger().error("Could not serialise event to elastic execution")
            raise

    @classmethod
    def from_message(cls, message, execution_context: ExecutionContext):
        try:
            schema = EventSchema()
            data = schema.loads(message)
            event = Event(**data)
            event._execution_context = execution_context
            return event
        except (marshmallow.exceptions.MarshmallowError, JSONDecodeError):
            LogManager._get_audit_logger().error("Error deserialising input event")
            raise
        except Exception:
            LogManager._get_audit_logger().error("Could not load event data")
            raise
