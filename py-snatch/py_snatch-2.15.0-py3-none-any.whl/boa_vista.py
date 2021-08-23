from dataclasses import dataclass
from typing import Any, Dict, Optional, Type

from loguru import logger
from marshmallow import EXCLUDE, Schema, fields, post_load, pre_load

from snatch.base.data import BaseData
from snatch.base.data_source import BaseSnatch
from snatch.base.schema import BaseSchema


@dataclass
class BoaVistaData(BaseData):
    """Boa Vista Data.

    Contains all data prospect from Boa Vista Data Source.

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

    Boa Vista Properties
    ====================
    * default_probability (float):      Default probability for TaxId.
    * score (int):                      Boa Vista Score for TaxId.
    * total_debts (float):              Boa Vista Total Debts registered.
    * tax_id_status (str):              TaxId status at Central Bank.
    """

    default_probability: Optional[float] = None
    score: Optional[int] = None
    total_debts: Optional[float] = None
    tax_id_status: Optional[str] = None


class BoaVistaSerializer(BaseSchema):
    default_probability = fields.Float(allow_none=True)
    score = fields.Integer(allow_none=True)
    total_debts = fields.Float(allow_none=True)
    tax_id_status = fields.Str(allow_none=True)
    payload = fields.Dict(allow_none=True)

    @pre_load
    def log_received_data(self, data, **kwargs) -> Dict[Any, Any]:
        logger.debug(f"Request Data received is: {data}")
        return data

    @post_load
    def make_data(self, data, **kwargs) -> BoaVistaData:
        logger.debug(f"Deserialized Data received is: {data}")
        new_data = BoaVistaData(**data)
        new_data.datasource_base_url = BoaVista.base_url
        return new_data

    class Meta:
        unknown = EXCLUDE


@dataclass
class BoaVista(BaseSnatch):
    default_timeout: int = 60
    default_max_days: int = 180
    base_url_key: str = "snatch.datasource_boa_vista_url"
    authorization_token_key: str = "snatch.boa_vista_secret_token"
    serializer_class: Type[Schema] = BoaVistaSerializer
