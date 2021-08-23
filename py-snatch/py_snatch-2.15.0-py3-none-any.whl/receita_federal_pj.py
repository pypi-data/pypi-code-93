from dataclasses import dataclass
from datetime import date
from typing import Any, Dict, List, Optional, Type

from loguru import logger
from marshmallow import EXCLUDE, Schema, fields, post_load, pre_load

from snatch.base.data import BaseData
from snatch.base.data_source import BaseSnatch
from snatch.base.schema import BaseSchema


@dataclass
class ReceitaFederalPJData(BaseData):
    """ReceitaFederalPJData Data.

    Contains all data prospect from Receita Federal Data Source.

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

    ReceitaFederalPJData Properties
    ===============================

    * official_name (str)               Company Official Name ("Razão Social").
    * trade_name (str)                  Company Trade Name ("Nome Fantasia").
    * foundation_date (date)            Company Foundation Date.
    * tax_regime (str)                  Tax Regime.
    * tax_status (str)                  Receita Federal Tax current status.
    * legal_nature_code (str)           Company Legal Nature Code.
    * legal_nature_description (str)    Company Legal Nature Description.
    * is_headquarter (bool)             Is Headquarter?
    * main_activity (str)               Company Main Activity Code ("CNAE code").
    * activities (List[str])            List of activities codes ("CNAE codes").

    """

    official_name: Optional[str] = None
    trade_name: Optional[str] = None
    foundation_date: Optional[date] = None
    tax_regime: Optional[str] = None
    tax_status: Optional[str] = None
    legal_nature_code: Optional[str] = None
    legal_nature_description: Optional[str] = None
    is_headquarter: Optional[bool] = None
    main_activity: Optional[str] = None
    activities: Optional[List[str]] = None


class ReceitaFederalPJSerializer(BaseSchema):
    official_name = fields.String(allow_none=True)
    trade_name = fields.String(allow_none=True)
    foundation_date = fields.Date(allow_none=True)
    tax_regime = fields.String(allow_none=True)
    tax_status = fields.String(allow_none=True)
    legal_nature_code = fields.String(allow_none=True)
    legal_nature_description = fields.String(allow_none=True)
    is_headquarter = fields.Boolean(allow_none=True)
    activities = fields.List(fields.String, allow_none=True)
    main_activity = fields.String(allow_none=True)
    payload = fields.Dict(allow_none=True)

    @pre_load
    def log_received_data(self, data, **kwargs) -> Dict[Any, Any]:
        logger.debug(f"Request Data received is: {data}")
        return data

    @post_load
    def make_data(self, data, **kwargs) -> ReceitaFederalPJData:
        logger.debug(f"Deserialized Data received is: {data}")
        new_data = ReceitaFederalPJData(**data)
        new_data.datasource_base_url = ReceitaFederalPJ.base_url
        return new_data

    class Meta:
        unknown = EXCLUDE


@dataclass
class ReceitaFederalPJ(BaseSnatch):
    default_timeout: int = 10
    default_max_days: int = 180
    base_url_key: str = "snatch.datasource_rf_url"
    authorization_token_key: str = "snatch.rf_secret_token"
    serializer_class: Type[Schema] = ReceitaFederalPJSerializer
