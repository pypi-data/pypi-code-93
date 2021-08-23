from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Type, TypedDict

from loguru import logger
from marshmallow import EXCLUDE, Schema, fields, post_load, pre_load

from snatch.base.data import BaseData
from snatch.base.data_source import BaseSnatch
from snatch.base.schema import BaseSchema


class ProtestMemberDict(TypedDict):
    person_tax_id: Optional[str]
    protests_flag: Optional[bool]
    status: Optional[str]
    payload: Optional[Dict[Any, Any]]


@dataclass
class ProtestData(BaseData):
    """Protest Data.

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
    * datasource_base_url (str)         Data Source Base Url.
    * data_type (str)                   DataSource Object Name.

    Protest Properties
    ==================

    * all_members_verified (bool)       True if all QSA members was checked. Some
                                        QSA members does not his CPF saved
                                        in BigDataCorp Database
    * members_protest (List[ProtestMemberDict]) The Protest Info for each
                                                QSA Person member.

    The Protest Member Dictionary
    =============================

    Each QSA Person Member are represented by a ProtestMemberDict dict
    type object. Each dictionary has the following keys:

    * person_tax_id (str)               QSA Member Personal TaxId (CPF).
    * protests_flag (bool)              Has Protest?
    * status (str)                      Protest Info.
    * payload (Dict)                    Response Payload from Datasource.
    """

    members_protest: Optional[List[ProtestMemberDict]] = None
    all_members_verified: Optional[bool] = None


class ProtestMemberDictSchema(Schema):
    person_tax_id = fields.String(allow_none=True)
    protests_flag = fields.Boolean(allow_none=True)
    status = fields.String(allow_none=True)
    payload = fields.Dict(allow_none=True)

    class Meta:
        unknown = EXCLUDE


class ProtestSerializer(BaseSchema):
    members_protest = fields.Nested(ProtestMemberDictSchema, many=True)
    all_members_verified = fields.Boolean(allow_none=True)
    payload = fields.Dict(allow_none=True)

    @pre_load
    def log_received_data(self, data, **kwargs) -> Dict[Any, Any]:
        logger.debug(f"Request Data received is: {data}")
        return data

    @post_load
    def make_data(self, data, **kwargs) -> ProtestData:
        logger.debug(f"Deserialized Data received is: {data}")
        new_data = ProtestData(**data)
        new_data.datasource_base_url = Protest.base_url
        return new_data

    class Meta:
        unknown = EXCLUDE


@dataclass
class Protest(BaseSnatch):
    default_timeout: int = 90
    default_max_days: int = 30
    base_url_key: str = "snatch.datasource_protest_url"
    authorization_token_key: str = "snatch.protest_secret_token"
    serializer_class: Type[Schema] = ProtestSerializer
