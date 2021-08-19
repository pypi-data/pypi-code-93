import os

from marshmallow import Schema, fields, post_load, pre_load, post_dump

from aide_sdk.model.resource import Resource
from aide_sdk.utils import file_storage


class ResourceSchema(Schema):
    content_type = fields.Str(load_only=True)
    format = fields.Str(load_only=True)
    type = fields.Method("generate_type_str", dump_only=True)
    file_path = fields.Str()
    namespace = fields.Str()

    def generate_type_str(self, obj):
        return f"{obj.format}/{obj.content_type}"

    @pre_load
    def update_file_paths(self, data, **kwargs):
        data['file_path'] = os.path.join(file_storage.mount_path, data.get('file_path'))
        return data

    @pre_load
    def expand_type(self, data, **kwargs):
        format, content_type = data['type'].split('/')
        data['content_type'] = content_type
        data['format'] = format
        del data['type']
        return data

    @post_dump
    def output_single_filepath(self, data, **kwargs):
        data['file_path'] = os.path.relpath(data.get('file_path'), file_storage.mount_path)
        return data

    @post_load
    def make_object(self, data, **kwargs):
        namespace = data.get('namespace')
        del data['namespace']
        resource = Resource(**data)
        resource.namespace = namespace
        return resource
