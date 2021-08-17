from marshmallow import Schema, fields


class DefinitionSchema(Schema):
    input = fields.String(description="APP input")
    output = fields.String(description="APP output")
