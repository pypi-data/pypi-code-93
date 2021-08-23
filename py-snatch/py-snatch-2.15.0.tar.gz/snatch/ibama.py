from dataclasses import dataclass
from typing import Any, Dict, Optional, Type

from loguru import logger
from marshmallow import EXCLUDE, Schema, fields, post_load, pre_load

from snatch.base.data import BaseData
from snatch.base.data_source import BaseSnatch
from snatch.base.schema import BaseSchema


@dataclass
class IbamaData(BaseData):
    """Ibama Data.

    Contains all data prospect from Ibama Data Source.

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

    Ibama Properties
    ====================
    * ibama_status (str):          Ibama Status Message for TaxId.
    """

    ibama_status: Optional[str] = None


class IbamaSerializer(BaseSchema):
    ibama_status = fields.Str(allow_none=True)
    payload = fields.Dict(allow_none=True)

    @pre_load
    def log_received_data(self, data, **kwargs) -> Dict[Any, Any]:
        logger.debug(f"Request Data received is: {data}")
        return data

    @post_load
    def make_data(self, data, **kwargs) -> IbamaData:
        logger.debug(f"Deserialized Data received is: {data}")
        new_data = IbamaData(**data)
        new_data.datasource_base_url = Ibama.base_url
        return new_data

    class Meta:
        unknown = EXCLUDE


@dataclass
class Ibama(BaseSnatch):
    default_timeout: int = 60
    default_max_days: int = 180
    base_url_key: str = "snatch.datasource_ibama_url"
    authorization_token_key: str = "snatch.ibama_secret_token"
    serializer_class: Type[Schema] = IbamaSerializer
