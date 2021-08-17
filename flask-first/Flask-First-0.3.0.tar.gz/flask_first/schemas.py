"""The module contains Marshmellow schemas for serializing the specification."""
from typing import Any

from marshmallow import fields
from marshmallow import pre_load
from marshmallow import Schema
from marshmallow import validate
from marshmallow import validates_schema
from marshmallow import ValidationError

VALUE_TYPES = ['boolean', 'object', 'array', 'number', 'string', 'integer']
VALUE_FORMATS = [
    'date-time',
    'date',
    'time',
    'duration',
    'email',
    'idn-email',
    'hostname',
    'idn-hostname',
    'ipv4',
    'ipv6',
    'uri',
    'uri-reference',
    'iri',
    'iri-reference',
    'uuid',
    'uri-template',
    'json-pointer',
    'relative-json-pointer',
    'regex',
    'int32',
    'int64',
    'float',
    'double',
    'byte',
    'binary',
    'password',
]

SECURITY_TYPES = ['apiKey', 'http', 'oauth2', 'openIdConnect']

MEDIA_TYPES = [
    '*/*',
    'application/json',
    'application/xml',
    'text/html',
    'text/plain',
    'multipart/form-data',
]

PARAMETER_LOCATIONS = ['path', 'query', 'header', 'cookie']
PARAMETER_STYLES = [
    'matrix',
    'label',
    'form',
    'simple',
    'spaceDelimited',
    'pipeDelimited',
    'deepObject',
]

METHODS = ['get', 'put', 'post', 'delete', 'options', 'head', 'patch', 'trace']

# Regexp`s.
PROPERTY_NAME = r'^[a-z_]{1}[a-z0-9_]+$'
PARAMETER_NAME = r'^[a-zA-Z/{}_\-0-9]+$'
ROUTE_PATH = r'^/[a-zA-Z/{}_\-0-9]+$'
RESPONSE_STATUS_CODE = r'^[0-9]{3}$|^default$'


def resolve_ref(ref: str, raw_spec: dict) -> dict:
    keys_from_ref = ref.split('/')[1:]

    value_from_ref = raw_spec
    for key in keys_from_ref:
        value_from_ref = value_from_ref[key]

    return value_from_ref


class BaseSchema(Schema):
    @pre_load
    def preprocess(self, data: Any, **kwargs) -> dict:
        if data.get('$ref'):
            self.resolve_reference(data)
        if isinstance(data.get('parameters'), list):
            self.parameters_to_dict(data)
        return data

    def resolve_reference(self, data: Any) -> None:
        data.update(resolve_ref(data['$ref'], self.context['raw_spec']))
        data.pop('$ref')

    def parameters_to_dict(self, data: Any) -> None:
        parameters = {}
        for param in data['parameters']:
            if param.get('$ref'):
                self.resolve_reference(param)
            parameters[param['name']] = param
        data['parameters'] = parameters


class ServerVariableObjectSchema(BaseSchema):
    enum = fields.List(fields.String())
    default = fields.String(required=True)
    description = fields.String()


class ServerObjectSchema(BaseSchema):
    url = fields.String(required=True)
    description = fields.String()
    variables = fields.Dict(fields.String(), fields.Nested(ServerVariableObjectSchema))


class SchemaObjectSchema(BaseSchema):
    _type = fields.String(data_key='type', validate=validate.OneOf(VALUE_TYPES))
    example = fields.Raw()
    minimum = fields.Float(strict=True)
    maximum = fields.Float(strict=True)
    minLength = fields.Integer(strict=True, validate=validate.Range(min=0))
    maxLength = fields.Integer(strict=True, validate=validate.Range(min=0))
    format = fields.String(validate=validate.OneOf(VALUE_FORMATS))
    required = fields.List(fields.String())
    additionalProperties = fields.Boolean()
    properties = fields.Dict(
        fields.String(validate=validate.Regexp(PROPERTY_NAME)), fields.Nested('SchemaObjectSchema')
    )
    items = fields.Nested('SchemaObjectSchema')
    description = fields.String()
    default = fields.Raw()
    enum = fields.List(fields.String())


class ExampleObjectSchema(BaseSchema):
    summary = fields.String()
    description = fields.String()
    value = fields.Raw()
    externalValue = fields.URL()


class MediaTypeObjectSchema(BaseSchema):
    schema = fields.Nested(SchemaObjectSchema)
    examples = fields.Dict(fields.String(required=True), fields.Nested(ExampleObjectSchema))


class RequestBodyObjectSchema(BaseSchema):
    description = fields.String()
    content = fields.Dict(
        fields.String(required=True, validate=validate.OneOf(MEDIA_TYPES)),
        fields.Nested(MediaTypeObjectSchema, required=True),
    )
    required = fields.Boolean()


class ResponseObjectSchema(RequestBodyObjectSchema):
    """Response is similar to request."""


class ParameterObjectSchema(BaseSchema):
    name = fields.String(required=True, validate=validate.Regexp(PARAMETER_NAME))
    _in = fields.String(data_key='in', required=True, validate=validate.OneOf(PARAMETER_LOCATIONS))
    description = fields.String()
    required = fields.Boolean()
    schema = fields.Nested(SchemaObjectSchema)
    reference = fields.String(data_key='$ref', load_only=True)
    style = fields.String(validate=validate.OneOf(PARAMETER_STYLES))

    @validates_schema
    def validate_required_field(self, data, **kwargs):
        if not data.get('required') and data['_in'] == 'path':
            raise ValidationError('Path parameter must be required!')


class OperationObjectSchema(BaseSchema):
    tags = fields.List(fields.String())
    summary = fields.String()
    description = fields.String()
    operationId = fields.String(validate=validate.Regexp(PROPERTY_NAME))
    parameters = fields.Dict(fields.String(required=True), fields.Nested(ParameterObjectSchema))
    requestBody = fields.Nested(RequestBodyObjectSchema)
    responses = fields.Dict(
        fields.String(required=True, validate=validate.Regexp(RESPONSE_STATUS_CODE)),
        fields.Nested(ResponseObjectSchema, required=True),
        required=True,
    )
    deprecated = fields.Boolean()
    security = fields.List(fields.Dict(fields.String(), fields.List(fields.String())))
    servers = fields.Nested(ServerObjectSchema, many=True)


class ContactObjectSchema(BaseSchema):
    name = fields.String()
    url = fields.URL()
    email = fields.Email()


class LicenseObjectSchema(BaseSchema):
    name = fields.String(required=True)
    url = fields.URL()


class InfoObjectSchema(BaseSchema):
    title = fields.String(required=True)
    description = fields.String()
    termsOfService = fields.URL()
    contact = fields.Nested(ContactObjectSchema)
    license = fields.Nested(LicenseObjectSchema)
    version = fields.String(required=True)


class OAuthFlowObjectSchema(BaseSchema):
    authorizationUrl = fields.URL(required=True)
    tokenUrl = fields.URL(required=True)
    refreshUrl = fields.URL()
    scopes = fields.Dict(fields.String(), fields.String(), required=True)


class OAuthFlowsObjectSchema(BaseSchema):
    implicit = fields.Nested(OAuthFlowObjectSchema)
    password = fields.Nested(OAuthFlowObjectSchema)
    clientCredentials = fields.Nested(OAuthFlowObjectSchema)
    authorizationCode = fields.Nested(OAuthFlowObjectSchema)


class SecuritySchemeObjectSchema(BaseSchema):
    type_ = fields.String(data_key='type', required=True, validate=validate.OneOf(SECURITY_TYPES))
    description = fields.String()
    name = fields.String()
    in_ = fields.String(data_key='in', validate=validate.OneOf(['query', 'header', 'cookie']))
    scheme = fields.String(validate=validate.OneOf(['basic', 'bearer', 'digest', 'oauth']))
    bearerFormat = fields.String()
    flows = fields.Nested(OAuthFlowsObjectSchema)
    openIdConnectUrl = fields.URL()

    @validates_schema
    def validate_api_key(self, data, **kwargs):
        if data['type_'] == 'apiKey':
            if not data.get('name'):
                raise ValidationError('Parameter <name> required with type <apiKey>!')

            if not data.get('in_'):
                raise ValidationError('Parameter <in> required with type <apiKey>!')

    @validates_schema
    def validate_http(self, data, **kwargs):
        if data['type_'] == 'http':
            if not data.get('scheme'):
                raise ValidationError('Parameter <scheme> required with type <http>!')

            if data.get('scheme') == 'bearer':
                if not data.get('bearerFormat'):
                    raise ValidationError(
                        'Parameter <bearerFormat> required with type <http> and scheme <bearer>!'
                    )

    @validates_schema
    def validate_oauth(self, data, **kwargs):
        if data['type_'] == 'oauth':
            if not data.get('flows'):
                raise ValidationError('Parameter <flows> required with type <oauth>!')

    @validates_schema
    def validate_open_id_connect_url(self, data, **kwargs):
        if data['type_'] == 'openIdConnect':
            if not data.get('openIdConnectUrl'):
                raise ValidationError(
                    'Parameter <openIdConnectUrl> required with type <openIdConnect>!'
                )


class ComponentsObjectSchema(BaseSchema):
    schemas = fields.Dict(fields.String(required=True), fields.Nested(SchemaObjectSchema))
    responses = fields.Dict(fields.String(required=True), fields.Nested(ResponseObjectSchema))
    parameters = fields.Dict(fields.String(required=True), fields.Nested(ParameterObjectSchema))
    requestBodies = fields.Dict(
        fields.String(required=True), fields.Nested(RequestBodyObjectSchema)
    )
    headers = fields.Raw()
    securitySchemes = fields.Dict(
        fields.String(required=True), fields.Nested(SecuritySchemeObjectSchema)
    )
    links = fields.Raw()
    callbacks = fields.Raw()


class TagObjectSchema(BaseSchema):
    name = fields.String(required=True)
    description = fields.String()


class OpenAPIObjectSchema(BaseSchema):
    openapi = fields.String(required=True)
    info = fields.Nested(InfoObjectSchema, required=True)
    servers = fields.Nested(ServerObjectSchema, many=True)
    paths = fields.Dict(
        fields.String(required=True, validate=validate.Regexp(ROUTE_PATH)),
        fields.Dict(
            fields.String(required=True, validate=validate.OneOf(METHODS)),
            fields.Nested(OperationObjectSchema, required=True),
            required=True,
        ),
        required=True,
    )
    components = fields.Nested(ComponentsObjectSchema)
    tags = fields.Nested(TagObjectSchema, many=True)
