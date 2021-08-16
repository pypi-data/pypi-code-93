from marshmallow import Schema, fields, post_load, post_dump

from aide_sdk.manifests.execution_context import ExecutionContext


class ExecutionSchema(Schema):
    model_uid = fields.Str()
    execution_uid = fields.UUID()
    clinical_review_received = fields.Bool(default=None)

    @post_dump
    def remove_none(self, data, **kwargs):
        if data['clinical_review_received'] is None:
            del data['clinical_review_received']
        return data

    @post_load
    def make_object(self, data, **kwargs):
        return ExecutionContext(**data)
