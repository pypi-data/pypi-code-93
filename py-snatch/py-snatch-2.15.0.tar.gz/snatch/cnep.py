from dataclasses import dataclass
from typing import Any, Dict, Optional, Type

from loguru import logger
from marshmallow import EXCLUDE, Schema, fields, post_load, pre_load

from snatch.base.data import BaseData
from snatch.base.data_source import BaseSnatch
from snatch.base.schema import BaseSchema


@dataclass
class CNEPData(BaseData):
    """CNEP Data.

    Contains all data prospect from CNEP Data Source.

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
    * legacy_data                       Data is from legacy database?

    CNEP Properties
    ====================
    * cnep_status (str):                CNEP Status for TaxId.
    """

    cnep_status: Optional[str] = None


class CNEPSerializer(BaseSchema):
    cnep_status = fields.Str(allow_none=True)
    payload = fields.List(fields.Dict, allow_none=True)

    @pre_load
    def log_received_data(self, data, **kwargs) -> Dict[Any, Any]:
        logger.debug(f"Request Data received is: {data}")
        if "payload" in data and isinstance(data["payload"], dict):
            data["payload"] = [data["payload"]]
        return data

    @post_load
    def make_data(self, data, **kwargs) -> CNEPData:
        logger.debug(f"Deserialized Data received is: {data}")
        new_data = CNEPData(**data)
        new_data.datasource_base_url = CNEP.base_url
        return new_data

    class Meta:
        unknown = EXCLUDE


@dataclass
class CNEP(BaseSnatch):
    default_timeout: int = 30 * 4
    default_max_days: int = 180
    base_url_key: str = "snatch.datasource_cnep_url"
    authorization_token_key: str = "snatch.cnep_secret_token"
    serializer_class: Type[Schema] = CNEPSerializer
