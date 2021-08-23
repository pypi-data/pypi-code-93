from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Type, TypedDict

from loguru import logger
from marshmallow import EXCLUDE, Schema, fields, post_load, pre_load

from snatch.base.data import BaseData
from snatch.base.data_source import BaseSnatch
from snatch.base.schema import BaseSchema


class QSADict(TypedDict):
    entity_name: Optional[str]
    entity_tax_id: Optional[str]
    entity_tax_id_type: Optional[str]
    relationship_type: Optional[str]
    relationship_name: Optional[str]
    relationship_level: Optional[str]
    relationship_source: Optional[str]
    relationship_status: Optional[str]
    relationship_start_date: Optional[datetime]
    relationship_end_date: Optional[datetime]


@dataclass
class QSAData(BaseData):
    """QSA Data.

    Contains all data prospect from QSA Data Source.

    Default Properties
    ==================

    * tax_id (str)                      The TaxId prospected.
                                        must be a valid CNPJ, formatted or not.
    * integration_status (str)          The current Integration Status, please check the
                                        `find_current_status` method for more info.
    * status_reason (str)               The human friendly reason for current status
    * prospect_date (datetime)          The prospect datetime.
    * payload (dict)                    Original payload received from prospection.
    * timeit (str)                      Time in seconds for retrieving data.
    * datasource_base_url (str)         Data Source Base Url
    * data_type (str)                   DataSource Object Name

    QSA Properties
    ==============

    * qsa_companies (List[QSADict])     The QSA Companies (relationship type:
                                        REPRESENTANTELEGAL, QSA or Ownership).
    * qsa_persons (List[QSADict])       The QSA Persons (relationship type:
                                        REPRESENTANTELEGAL, QSA or Ownership).
    * is_family_company (bool)          Is a Family Company?
    * is_family_operated (bool)         Is Family Operated?
    * total_relationships (int)         Total Relationships as per DataSource response.
    * total_owners (int)                Total Owners as per DataSource response.
    * total_employees (int)             Total Employees as per DataSource response.
    * total_owned (int)                 Total Owned as per DataSource response.

    The QSA Dictionary
    ==================

    Each QSA Entity (company or Person) are represented by a QSADict dict
    type object. Each dictionary has the following keys:

    * entity_name (str):                QSA Entity Name
    * entity_tax_id (str):              QSA Entity TaxId
    * entity_tax_id_type (str):         QSA Entity TaxId Type
    * relationship_type (str):          The Relationship Type between the Entity
                                        and original TaxId
    * relationship_name (str):          The Relationship Name between the Entity
                                        and original TaxId
    * relationship_level (str):         The Relationship Level between the Entity
                                        and original TaxId
    * relationship_source (str):        The Relationship Original Source Provider
    * relationship_status (str):        The Current Relationship Status between
                                        the Entity and original TaxId (values are:
                                        RELATED, CURRENT, HISTORICAL)
    * relationship_start_date (datetime): The Relationship Start Date between the Entity
                                        and original TaxId
    * relationship_end_date (datetime): The Relationship End Date between the Entity
                                        and original TaxId
    * qsa_company_names (List[str]):    QSA Company Name List
    * qsa_person_names (List[str]):     QSA Person Name List
    * qsa_company_tax_ids (List[str]):  QSA Company TaxId List
    * qsa_person_tax_ids (List[str]):   QSA Person TaxId List
    * qsa_total_members (int):          QSA Total Members Count
    * qsa_company_members (int):        QSA Total Companies Count
    * qsa_person_members (int):         QSA Total Persons Count
    """

    qsa_companies: Optional[List[QSADict]] = None
    qsa_persons: Optional[List[QSADict]] = None
    is_family_company: Optional[bool] = None
    is_family_operated: Optional[bool] = None
    total_relationships: Optional[int] = None
    total_owners: Optional[int] = None
    total_employees: Optional[int] = None
    total_owned: Optional[int] = None
    qsa_company_names: Optional[List[str]] = None
    qsa_person_names: Optional[List[str]] = None
    qsa_company_tax_ids: Optional[List[str]] = None
    qsa_person_tax_ids: Optional[List[str]] = None
    qsa_total_members: Optional[int] = None
    qsa_company_members: Optional[int] = None
    qsa_person_members: Optional[int] = None


class QSADictSchema(Schema):
    entity_name = fields.String(allow_none=True)
    entity_tax_id = fields.String(allow_none=True)
    entity_tax_id_type = fields.String(allow_none=True)
    relationship_type = fields.String(allow_none=True, data_key="relation_type")
    relationship_name = fields.String(allow_none=True, data_key="relation_name")
    relationship_level = fields.String(allow_none=True, data_key="relation_level")
    relationship_source = fields.String(
        allow_none=True, data_key="relation_data_source"
    )
    relationship_status = fields.String(allow_none=True, data_key="relation_status")
    relationship_start_date = fields.DateTime(
        allow_none=True, data_key="relation_start_date"
    )
    relationship_end_date = fields.DateTime(
        allow_none=True, data_key="relation_end_date"
    )

    @pre_load
    def populate_entity_fields(self, data, **kwargs) -> Dict[Any, Any]:
        if data.get("entity"):
            data["entity_name"] = data["entity"]["entity_name"]
            data["entity_tax_id"] = data["entity"]["tax_id"]
            data["tax_id_type"] = data["entity"]["tax_id_type"]
        return data

    class Meta:
        unknown = EXCLUDE


class QSASerializer(BaseSchema):
    qsa_companies = fields.Nested(QSADictSchema, many=True)
    qsa_persons = fields.Nested(QSADictSchema, many=True)
    is_family_company = fields.Boolean(allow_none=True)
    is_family_operated = fields.Boolean(allow_none=True)
    total_relationships = fields.Integer(allow_none=True)
    total_owners = fields.Integer(allow_none=True)
    total_employees = fields.Integer(allow_none=True)
    total_owned = fields.Integer(allow_none=True)
    payload = fields.Dict(allow_none=True)
    qsa_company_names = fields.List(fields.String, allow_none=True)
    qsa_person_names = fields.List(fields.String, allow_none=True)
    qsa_company_tax_ids = fields.List(fields.String, allow_none=True)
    qsa_person_tax_ids = fields.List(fields.String, allow_none=True)
    qsa_total_members = fields.Integer(allow_none=True)
    qsa_company_members = fields.Integer(allow_none=True)
    qsa_person_members = fields.Integer(allow_none=True)

    @pre_load
    def log_received_data(self, data, **kwargs) -> Dict[Any, Any]:
        logger.debug(f"Request Data received is: {data}")
        return data

    @post_load
    def make_data(self, data, **kwargs) -> QSAData:
        logger.debug(f"Deserialized Data received is: {data}")
        new_data = QSAData(**data)
        new_data.datasource_base_url = QSA.base_url
        return new_data

    class Meta:
        unknown = EXCLUDE


@dataclass
class QSA(BaseSnatch):
    default_timeout: int = 10
    default_max_days: int = 180
    base_url_key: str = "snatch.datasource_qsa_url"
    authorization_token_key: str = "snatch.qsa_secret_token"
    serializer_class: Type[Schema] = QSASerializer
