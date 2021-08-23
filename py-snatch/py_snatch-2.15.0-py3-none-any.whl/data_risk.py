from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Type, TypedDict

from loguru import logger
from marshmallow import EXCLUDE, Schema, fields, post_load, pre_load

from snatch.base.data import BaseData
from snatch.base.data_source import BaseSnatch
from snatch.base.schema import BaseSchema


class DataRiskMemberDict(TypedDict):
    person_tax_id: Optional[str]
    score: Optional[int]
    payload: Optional[Dict[Any, Any]]


@dataclass
class DataRiskData(BaseData):
    """Data Risk Data.

    Contains all data prospect from Data Risk Data Source.

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

    * members_score (List[DataRiskMemberDict])  The Data Risk Members (from QSA
                                                personal members).

    The Data Risk Member Dictionary
    ===============================

    Each Data Risk Member are represented by a DataRiskMemberDict dict
    type object. Each dictionary has the following keys:

    * person_tax_id (str):              Data Risk Member personal TaxId ("CPF").
    * score (int):                      Data Risk Member Score.
    * payload (dict)                    Original payload received from prospection.
    """

    members_score: Optional[List[DataRiskMemberDict]] = None


class DataRiskMemberDictSchema(Schema):
    person_tax_id = fields.String(allow_none=True)
    score = fields.Integer(allow_none=True)
    payload = fields.Dict(allow_none=True)

    class Meta:
        unknown = EXCLUDE


class DataRiskSerializer(BaseSchema):
    members_score = fields.Nested(DataRiskMemberDictSchema, many=True)
    payload = fields.Dict(allow_none=True)

    @pre_load
    def log_received_data(self, data, **kwargs) -> Dict[Any, Any]:
        logger.debug(f"Request Data received is: {data}")
        return data

    @post_load
    def make_data(self, data, **kwargs) -> DataRiskData:
        logger.debug(f"Deserialized Data received is: {data}")
        new_data = DataRiskData(**data)
        new_data.datasource_base_url = DataRisk.base_url
        return new_data

    class Meta:
        unknown = EXCLUDE


@dataclass
class DataRisk(BaseSnatch):
    default_timeout: int = 10
    default_max_days: int = 180
    base_url_key: str = "snatch.datasource_data_risk_url"
    authorization_token_key: str = "snatch.data_risk_secret_token"
    serializer_class: Type[Schema] = DataRiskSerializer
