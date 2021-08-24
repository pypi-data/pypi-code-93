# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 CERN.
#
# My site is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""JSON Schemas."""

from nr_datasets_metadata.marshmallow import DatasetMetadataSchemaV1
from oarepo_communities.marshmallow import OARepoCommunitiesMixin
from oarepo_fsm.marshmallow import FSMRecordSchemaMixin


class NRDatasetMetadataSchemaV1(OARepoCommunitiesMixin,
                                FSMRecordSchemaMixin,
                                DatasetMetadataSchemaV1):
    """Schema for NR dataset record metadata."""
