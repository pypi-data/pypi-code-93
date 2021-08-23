from dataclasses import dataclass
from typing import Optional, Type

from marshmallow import EXCLUDE, Schema, fields, post_load

from snatch.base.data import BaseData
from snatch.base.data_source import BaseSnatch
from snatch.base.schema import BaseSchema


@dataclass
class PepData(BaseData):
    """PEP Data.

    Contains all data prospect from PEP Data Source.

    Default Properties
    ==================
    * tax_id (str):                     The TaxId prospected.
                                        must be a valid CNPJ, formatted or not.
    * integration_status (str):         The current Integration Status, please check the
                                        `find_current_status` method for more info.
    * status_reason (str):              The human friendly reason for current status
    * prospect_date (datetime):         The prospect datetime.
    * payload (dict):                   Original payload received from prospection.
    * timeit                            Time in seconds for retrieving data.
    * datasource_base_url               Data Source Base Url

    PEP Properties
    ====================
    * cgu_pep_confidence (int):      PEP confidence integer for TaxId.
    * cgu_pep_result (str):          PEP Result Message for TaxId.
    """

    cgu_pep_confidence: Optional[int] = None
    cgu_pep_result: Optional[str] = None


class PepSerializer(BaseSchema):
    cgu_pep_confidence = fields.Integer(allow_none=True)
    cgu_pep_result = fields.Str(allow_none=True)
    payload = fields.Dict(allow_none=True)

    @post_load
    def make_data(self, data, **kwargs):
        new_data = PepData(**data)
        new_data.datasource_base_url = PEP.base_url
        return new_data

    class Meta:
        unknown = EXCLUDE


@dataclass
class PEP(BaseSnatch):
    default_timeout: int = 60
    default_max_days: int = 180
    base_url_key: str = "snatch.datasource_pep_url"
    authorization_token_key: str = "snatch.pep_secret_token"
    serializer_class: Type[Schema] = PepSerializer
