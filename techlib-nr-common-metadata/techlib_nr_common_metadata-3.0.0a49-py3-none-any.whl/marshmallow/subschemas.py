from invenio_records_rest.schemas import StrictKeysMixin
from invenio_records_rest.schemas.fields import SanitizedUnicode
from marshmallow import validates, ValidationError, validates_schema
from marshmallow.fields import List, URL, Nested, Url, Boolean, Integer, Date, DateTime
from marshmallow.validate import Length
from oarepo_multilingual.marshmallow import MultilingualStringV2
from oarepo_taxonomies.marshmallow import TaxonomyField

from nr_common_metadata.marshmallow.fields import ISBN, ISSN, DOI, RIV, Year, OAI


class TitledMixin:
    title = MultilingualStringV2()


class RelatedURISchema(StrictKeysMixin):
    coar = SanitizedUnicode()
    eprint = SanitizedUnicode()
    vocabs = SanitizedUnicode()


class AccessRightsMixin:
    relatedURI = Nested(RelatedURISchema)


class FunderMixin:
    funderISVaVaICode = SanitizedUnicode()


class RelatedIDSchema(StrictKeysMixin):
    RID = SanitizedUnicode()
    DOI = DOI()
    ISVaVaI = SanitizedUnicode()


class InstitutionsMixin:
    relatedID = Nested(RelatedIDSchema)
    aliases = List(SanitizedUnicode())
    ico = SanitizedUnicode()
    url = Url()
    provider = Boolean(missing=False)
    formerNames = List(SanitizedUnicode())


class CountryCodeSchema(StrictKeysMixin):
    alpha2 = SanitizedUnicode(validate=Length(equal=2))
    alpha3 = SanitizedUnicode(validate=Length(equal=3))
    number = SanitizedUnicode()


class CountryMixin:
    code = Nested(CountryCodeSchema)


class RightsRelated(StrictKeysMixin):
    uri = URL()


class RightsMixin:
    icon = Url()
    related = Nested(RightsRelated)


class SeriesMixin:
    seriesTitle = SanitizedUnicode(required=True)
    seriesVolume = SanitizedUnicode(required=True)


class SubjectMixin:
    relatedURI = List(Url)
    DateCreated = DateTime()
    DateRevised = DateTime()
    DateEstablished = DateTime()


class PSHMixin:
    altLabel = MultilingualStringV2()


class CZMeshMixin:
    TreeNumberList = List(SanitizedUnicode())


class MedvikMixin:
    pass


class PersonSchema(StrictKeysMixin):
    name = SanitizedUnicode(required=True)
    ORCID = SanitizedUnicode()
    scopusID = SanitizedUnicode()
    researcherID = SanitizedUnicode()  # WOS ID
    czenasAutID = SanitizedUnicode()
    vedidk = SanitizedUnicode()
    institutionalID = SanitizedUnicode()  # TODO: vložit prefix instituce


class ContributorMixin:
    dataCiteCode = SanitizedUnicode()
    marcCode = SanitizedUnicode()


class ContributorSchema(PersonSchema):
    role = TaxonomyField(mixins=[TitledMixin, ContributorMixin], required=True)


class RecordIdentifier(StrictKeysMixin):
    nuslOAI = OAI()
    nrcrHandle = Url()
    nrcrOAI = OAI()
    originalRecord = Url()
    originalRecordOAI = OAI()
    catalogueSysNo = SanitizedUnicode()


class WorkIdentifersSchema(StrictKeysMixin):
    isbn = List(ISBN())
    issn = List(ISSN())
    doi = DOI()
    RIV = RIV()


class FundingReferenceSchema(StrictKeysMixin):
    projectID = SanitizedUnicode()
    projectName = SanitizedUnicode()
    fundingProgram = SanitizedUnicode()
    funder = TaxonomyField(mixins=[FunderMixin, TitledMixin])

    @validates_schema
    def required_fields(self, data, **kwargs):
        if data.get("projectID"):
            if not data.get("funder"):
                raise ValidationError("Funder is required")


class PublicationPlaceSchema(StrictKeysMixin):
    place = SanitizedUnicode()
    country = TaxonomyField(mixins=[TitledMixin, CountryMixin])

    # @validates_schema
    # def required_fields(self, data, **kwargs):
    #     if data.get("place"):
    #         if not data.get("country"):
    #             raise ValidationError("Country is required")


class RelatedItemSchema(StrictKeysMixin):
    itemTitle = SanitizedUnicode(required=True)
    itemDOI = DOI()
    itemISBN = List(ISBN())
    itemISSN = List(ISSN())
    itemURL = URL()
    itemYear = Year()
    itemVolume = SanitizedUnicode()
    itemIssue = SanitizedUnicode()
    itemStartPage = SanitizedUnicode()
    itemEndPage = SanitizedUnicode()
    itemRelationType = TaxonomyField(mixins=[TitledMixin], required=True)

    @validates_schema
    def required_journal(self, data, **kwargs):
        if data.get("ISSN") or data.get("itemVolume") or data.get("itemIssue") or data.get(
                "itemStartPage") or data.get("itemEndPage"):
            journal_keys = ["itemVolume", "itemIssue", "itemStartPage", "itemEndPage"]
            for key in data.keys():
                if key in journal_keys:
                    journal_keys.pop(journal_keys.index(key))
            if len(journal_keys) > 0:
                raise ValidationError(f"Required field(s) is/are missing: {journal_keys}")

    @validates_schema
    def validate_pages(self, data, **kwargs):
        start_page = data.get("itemStartPage")
        end_page = data.get("itemEndPage")
        if start_page and end_page:
            if int(start_page) > int(end_page):
                raise ValidationError(
                    f"Start page ({start_page}) must be smaller than end page ({end_page})")


class SeriesSchema(StrictKeysMixin):
    seriesTitle = SanitizedUnicode(required=True)
    seriesVolume = SanitizedUnicode()


class RulesExceptionsSchema(StrictKeysMixin):
    path = SanitizedUnicode()
    element = SanitizedUnicode()
    phase = SanitizedUnicode()
    exception = SanitizedUnicode()