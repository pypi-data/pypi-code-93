from marshmallow import fields, post_load

from aide_sdk.model.origin import Origin
from aide_sdk.model.dicom_origin import DicomOrigin
from aide_sdk.messaging.schemas.resource import ResourceSchema
from aide_sdk.logger.logger import LogManager


def choose_origin_class_deserialisation(object_dict, parent_object_dict):
    type_to_schema = {
        'dicom': DicomOriginSchema
    }
    try:
        type_str = object_dict['type'].split('/')[0]
        if type_str in type_to_schema:
            return type_to_schema[type_str]()
    except Exception:
        LogManager._get_audit_logger().exception("Could not determine origin type")
        raise

    return OriginSchema()  # Default


def choose_origin_class_serialisation(base_object, parent_obj):
    class_to_schema = {
        Origin.__name__: OriginSchema,
        DicomOrigin.__name__: DicomOriginSchema
    }
    object_type = base_object.__class__.__name__
    if object_type in class_to_schema:
        return class_to_schema[object_type]()

    LogManager._get_audit_logger().error("Trying to serialise unknown origin")
    raise ValueError()


class OriginSchema(ResourceSchema):
    received_timestamp = fields.DateTime()
    patient_id = fields.Str(data_key='patientID')


class DicomOriginSchema(OriginSchema):
    study_uid = fields.Str(data_key="studyUID")
    _series = fields.List(fields.Dict, data_key="series")

    @post_load
    def make_object(self, data, **kwargs):
        namespace = data.get('namespace')
        del data['namespace']
        origin = DicomOrigin(**data)
        origin.namespace = namespace
        return origin
