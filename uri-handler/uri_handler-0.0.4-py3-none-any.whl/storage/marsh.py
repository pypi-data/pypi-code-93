"""
Drain the marsh
"""
import collections

import marshmallow

import uri_handler.errors


# TODO test timing on these w/ overpolulated dicts/toastedmarshmallow
class S3SessionSchema(marshmallow.Schema):
    aws_access_key_id = marshmallow.fields.String(required=False)
    aws_secret_access_key = marshmallow.fields.String(required=False)
    aws_session_token = marshmallow.fields.String(required=False)
    region_name = marshmallow.fields.String(required=False)
    profile_name = marshmallow.fields.String(required=False)
    # botocore_session = BotoSession(required=False)


# session and resourceschemas have overp
class S3ResourceSchema(marshmallow.Schema):
    endpoint_url = marshmallow.fields.String(required=False)
    aws_access_key_id = marshmallow.fields.String(required=False)
    aws_secret_access_key = marshmallow.fields.String(required=False)
    aws_session_token = marshmallow.fields.String(required=False)
    region_name = marshmallow.fields.String(required=False)


s3session_schema = S3SessionSchema()
s3resource_schema = S3ResourceSchema()


def load_schema_dict(input_d, schema):
    res = schema.dump({k: v[-1] for k, v in input_d.items()})
    try:
        if res.errors:
            raise uri_handler.errors.UriHandlerException(
                "Error parsing params {} with {}".format(
                    input_d, schema))
        else:
            return res.data
    except AttributeError:
        return res


def load_s3session_dict(input_d):
    return load_schema_dict(input_d, s3session_schema)


def load_s3resource_dict(input_d):
    return load_schema_dict(input_d, s3resource_schema)
    # return dict(s3resource_schema.dump(
    #     {k: v[-1] for k, v in input_d.items()}) or {})
