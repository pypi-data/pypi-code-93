from flask import url_for
from invenio_records_files.api import Record
from oarepo_communities.converters import CommunityPIDValue
from oarepo_communities.proxies import current_oarepo_communities
from oarepo_communities.record import CommunityRecordMixin
from oarepo_invenio_model import InheritedSchemaRecordMixin
from oarepo_records_draft.record import InvalidRecordAllowedMixin, DraftRecordMixin
from oarepo_validate import SchemaKeepingRecordMixin, MarshmallowValidatedRecordMixin, FilesKeepingRecordMixin

from .constants import published_index_name, draft_index_name, \
    all_datasets_index_name, DATASETS_PREFERRED_SCHEMA, DATASETS_ALLOWED_SCHEMAS
from .marshmallow import NRDatasetMetadataSchemaV1


class DatasetBaseRecord(SchemaKeepingRecordMixin,
                        FilesKeepingRecordMixin,
                        MarshmallowValidatedRecordMixin,
                        InheritedSchemaRecordMixin,
                        CommunityRecordMixin,
                        Record):
    ALLOWED_SCHEMAS = DATASETS_ALLOWED_SCHEMAS
    PREFERRED_SCHEMA = DATASETS_PREFERRED_SCHEMA
    MARSHMALLOW_SCHEMA = NRDatasetMetadataSchemaV1


class PublishedDatasetRecord(InvalidRecordAllowedMixin, DatasetBaseRecord):
    index_name = published_index_name

    @property
    def canonical_url(self):
        return url_for('invenio_records_rest.datasets-community_item',
                       pid_value=CommunityPIDValue(
                           self['id'],
                           current_oarepo_communities.get_primary_community_field(self)),
                       _external=True)


class DraftDatasetRecord(DraftRecordMixin, DatasetBaseRecord):
    index_name = draft_index_name

    @property
    def canonical_url(self):
        return url_for('invenio_records_rest.draft-datasets-community_item',
                       pid_value=CommunityPIDValue(
                           self['id'],
                           current_oarepo_communities.get_primary_community_field(self)),
                       _external=True)


class AllDatasetRecord(SchemaKeepingRecordMixin, CommunityRecordMixin, Record):
    ALLOWED_SCHEMAS = DATASETS_ALLOWED_SCHEMAS
    PREFERRED_SCHEMA = DATASETS_PREFERRED_SCHEMA
    index_name = all_datasets_index_name
    # TODO: better canonical url based on if the class is published or not
