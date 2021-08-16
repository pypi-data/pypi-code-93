from marshmallow import Schema, fields
from aide_sdk.messaging.schemas.event import EventSchema


class ExecutionContextSchema(Schema):
    execution_uid = fields.UUID()
    model_name = fields.Str()
    model_uid = fields.Str()
    model_version = fields.Str()
    model_description = fields.Str()
    predicate = fields.Str()
    mode = fields.Str()


class TimestampSchema(Schema):
    received_at = fields.DateTime()
    inference_started = fields.DateTime()
    inference_finished = fields.DateTime()


class StatusSchema(Schema):
    status = fields.Str()
    message = fields.Str(required=False, allow_none=False)


class EventExecutionSchema(Schema):
    correlation_id = fields.Function(lambda event: event.correlation_id)
    model = fields.Method('get_model')
    event = fields.Method('get_event')
    result = fields.Method('get_result')
    timestamp = fields.Method('get_timestamps')

    def get_model(self, event, **kwargs):
        return ExecutionContextSchema().dump(event._execution_context)

    def get_event(self, event):
        return EventSchema().dump(event)

    def get_result(self, event):
        d = {'status': 'success'}
        message = None
        if event._operator_context._failure:
            d['status'] = "fail"
            message = event._operator_context._failure_message
        if event._operator_context._error:
            # Errors override failures. If a model errored it can't have failed.
            d['status'] = "error"
            message = event._operator_context._error_message

        if message:
            d['message'] = message

        return StatusSchema().dump(d)

    def get_timestamps(self, event):
        return TimestampSchema().dump({
            'received_at': event.origin.received_timestamp,
            'inference_started': event.start_time,
            'inference_finished': event.end_time,
        })
