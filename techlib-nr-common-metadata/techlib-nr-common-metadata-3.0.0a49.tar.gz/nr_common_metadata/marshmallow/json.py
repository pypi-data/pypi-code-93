# # -*- coding: utf-8 -*-
# #
# # Copyright (C) 2019 CERN.
# #
# # My site is free software; you can redistribute it and/or modify it under
# # the terms of the MIT License; see LICENSE file for more details.
#
# """JSON Schemas."""
#
from __future__ import absolute_import, print_function

from invenio_records_rest.schemas import StrictKeysMixin
from invenio_records_rest.schemas.fields import SanitizedUnicode
from marshmallow import post_load, ValidationError, pre_load
from marshmallow.fields import Nested, Url, Boolean, List
from marshmallow.validate import Length
from oarepo_multilingual.marshmallow import MultilingualStringV2
from oarepo_taxonomies.marshmallow import TaxonomyField

from nr_common_metadata.marshmallow.fields import NRDate
from nr_common_metadata.marshmallow.subschemas import PersonSchema, ContributorSchema, \
    WorkIdentifersSchema, FundingReferenceSchema, PublicationPlaceSchema, RelatedItemSchema, \
    TitledMixin, AccessRightsMixin, InstitutionsMixin, RightsMixin, SubjectMixin, \
    PSHMixin, CZMeshMixin, MedvikMixin, RecordIdentifier, SeriesSchema, RulesExceptionsSchema


#


class CommonMetadataSchemaV2(StrictKeysMixin):
    """Schema for the record metadata."""

    abstract = MultilingualStringV2()
    accessibility = MultilingualStringV2()
    accessRights = TaxonomyField(mixins=[TitledMixin, AccessRightsMixin], required=True)
    creator = List(Nested(PersonSchema), required=True)
    contributor = List(Nested(ContributorSchema))
    dateIssued = NRDate(required=True)
    dateModified = NRDate()
    resourceType = TaxonomyField(mixins=[TitledMixin], required=True)
    extent = List(SanitizedUnicode())  # TODO: pokud nemáme extent, spočítat z PDF - asi nepůjde
    externalLocation = Url()
    control_number = SanitizedUnicode(required=True)
    recordIdentifiers = Nested(RecordIdentifier)
    workIdentifiers = Nested(WorkIdentifersSchema)
    isGL = Boolean()
    language = TaxonomyField(mixins=[TitledMixin], required=True)
    note = List(SanitizedUnicode())
    fundingReference = List(Nested(FundingReferenceSchema))
    provider = TaxonomyField(mixins=[TitledMixin, InstitutionsMixin], required=True)
    entities = TaxonomyField(mixins=[TitledMixin, InstitutionsMixin], many=True)
    publicationPlace = Nested(PublicationPlaceSchema)
    publisher = List(SanitizedUnicode())
    relatedItem = List(Nested(RelatedItemSchema))
    rights = TaxonomyField(mixins=[TitledMixin, RightsMixin], many=True)
    series = List(Nested(SeriesSchema))
    subject = TaxonomyField(mixins=[TitledMixin, SubjectMixin, PSHMixin, CZMeshMixin, MedvikMixin],
                            many=True)
    keywords = List(MultilingualStringV2())
    title = List(MultilingualStringV2(required=True), required=True, validate=Length(min=1))
    titleAlternate = List(MultilingualStringV2())
    rulesExceptions = List(Nested(RulesExceptionsSchema))

    @pre_load
    def check_keyword(self, data, **kwargs):
        keywords = data.get("keywords", [])
        if isinstance(keywords, dict):
            if "error" in keywords:
                raise ValidationError(keywords["error"])
        return data

    @post_load
    def check_language(self, data, **kwargs):
        language = data.get("language")
        if not language:
            raise ValidationError("Language is required field", field_name="language")
        return data

    @post_load
    def copy_to_entities(self, data, **kwargs):
        entities = data.get("entities")
        if not entities:
            data["entities"] = data["provider"]
        return data

    @post_load
    def rules_exceptions(self, data, **kwargs):
        if "rulesExceptions" in data:
            raise ValidationError(f"Some rules raises exception: {data['rulesExceptions']}")
        return data
