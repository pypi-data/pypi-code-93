import uuid

from flask import make_response
from invenio_access.permissions import Permission, any_user, authenticated_user
from invenio_indexer.api import RecordIndexer
from invenio_pidstore.providers.recordid import RecordIdProvider
from invenio_records.api import Record
from invenio_records_rest.utils import allow_all
from oarepo_actions.decorators import action
from oarepo_communities.record import CommunityRecordMixin
from oarepo_fsm.mixins import FSMMixin
from oarepo_validate import MarshmallowValidatedRecordMixin, SchemaKeepingRecordMixin

from .constants import SAMPLE_ALLOWED_SCHEMAS, SAMPLE_PREFERRED_SCHEMA
from .marshmallow import SampleSchemaV1


class SampleRecord(SchemaKeepingRecordMixin,
                   MarshmallowValidatedRecordMixin,
                   CommunityRecordMixin, FSMMixin,
                   Record):
    ALLOWED_SCHEMAS = SAMPLE_ALLOWED_SCHEMAS
    PREFERRED_SCHEMA = SAMPLE_PREFERRED_SCHEMA
    MARSHMALLOW_SCHEMA = SampleSchemaV1

    @property
    def canonical_url(self):
        return 'https://127.0.0.1:5000/cesnet/datasets/dat-7w607-k0s56'

    _schema = "sample/sample-v1.0.0.json"
    def validate(self, **kwargs):
        return super().validate(**kwargs)
