from dataclasses import dataclass
from datetime import date
from typing import Any, Dict, Optional, Type

from loguru import logger
from marshmallow import EXCLUDE, Schema, fields, post_load, pre_load

from snatch.base.data import BaseData
from snatch.base.data_source import BaseSnatch
from snatch.base.schema import BaseSchema


@dataclass
class BancoCentralData(BaseData):
    """Banco Central Data.

    Contains all data prospect from Banco Central Data Source.

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

    Banco Central Properties
    ========================

    * scr_code (str)                    Banco Central SCR Code.
    * tax_id (str)                      Customer TaxId (CNPJ).
    * data_base_year (int)              Data-Base Year.
    * data_base_month (int)             Data-Base Month.
    * customer_code (str)               Customer Code.
    * ifs_count (int)                   Financial Institutions count.
    * operation_count (int)             Operations count.
    * relation_start_date (date)        Relationship Start Date.
    * source (str)                      Data Source Name.
    * due_total (float)                 Due Amount Total.
    * due_30 (float)                    Due Amount up to 30d and past 14d.
    * due_60 (float)                    Due Amount up to 60d.
    * due_90 (float)                    Due Amount up to 90d.
    * due_180 (float)                   Due Amount up to 180d.
    * due_360 (float)                   Due Amount up to 360d.
    * due_past_360 (float)              Due Amount past 360d.
    * due_no_date (float)               Due Amount with no date specified.
    * past_due_total (float)            Past Due Amount Total.
    * past_due_30 (float)               Past Due Amount up to 30d and past 14d.
    * past_due_60 (float)               Past Due Amount up to 60d.
    * past_due_90 (float)               Past Due Amount up to 90d.
    * past_due_180 (float)              Past Due Amount up to 180d.
    * past_due_360 (float)              Past Due Amount up to 360d.
    * past_due_past_360 (float)         Past Due Amount past 360d.
    * loss_total (float)                Total Loss Amount.
    * loss_12 (float)                   Loss Amount up to 12m.
    * loss_48 (float)                   Loss Amount greater than 12m.
    * credit_portfolio (float)          Credit Portfolio Amount.
    * total_responsibility (float)      Total Responsibility Amount.
    * credit_limit_total (float)        Total Credit Limit Amount.
    * credit_limit_360 (float)          Credit Limit Amount up to 360d.
    * credit_limit_past_360 (float)     Credit Limit Amount past 360d.
    * guarantor_indirect_risk (float)   Indirect Risk as Guarantor Amount.
    * risk_total (float)                Total Risk Amount.
    """

    scr_code: Optional[str] = None
    tax_id: Optional[str] = None
    data_base_year: Optional[int] = None
    data_base_month: Optional[int] = None
    customer_code: Optional[str] = None
    ifs_count: Optional[int] = None
    operation_count: Optional[int] = None
    relation_start_date: Optional[date] = None
    source: Optional[str] = None
    due_total: Optional[float] = None
    due_30: Optional[float] = None
    due_60: Optional[float] = None
    due_90: Optional[float] = None
    due_180: Optional[float] = None
    due_360: Optional[float] = None
    due_past_360: Optional[float] = None
    due_no_date: Optional[float] = None
    past_due_total: Optional[float] = None
    past_due_30: Optional[float] = None
    past_due_60: Optional[float] = None
    past_due_90: Optional[float] = None
    past_due_180: Optional[float] = None
    past_due_360: Optional[float] = None
    past_due_past_360: Optional[float] = None
    loss_total: Optional[float] = None
    loss_12: Optional[float] = None
    loss_48: Optional[float] = None
    credit_portfolio: Optional[float] = None
    total_responsibility: Optional[float] = None
    credit_limit_total: Optional[float] = None
    credit_limit_360: Optional[float] = None
    credit_limit_past_360: Optional[float] = None
    guarantor_indirect_risk: Optional[float] = None
    risk_total: Optional[float] = None


class BancoCentralSerializer(BaseSchema):
    scr_code = fields.String(allow_none=True)
    tax_id = fields.String(allow_none=True)
    data_base_year = fields.Integer(allow_none=True)
    data_base_month = fields.Integer(allow_none=True)
    customer_code = fields.String(allow_none=True)
    ifs_count = fields.Integer(allow_none=True)
    operation_count = fields.Integer(allow_none=True)
    relation_start_date = fields.Date(allow_none=True)
    source = fields.String(allow_none=True)
    due_total = fields.Float(allow_none=True)
    due_30 = fields.Float(allow_none=True)
    due_60 = fields.Float(allow_none=True)
    due_90 = fields.Float(allow_none=True)
    due_180 = fields.Float(allow_none=True)
    due_360 = fields.Float(allow_none=True)
    due_past_360 = fields.Float(allow_none=True)
    due_no_date = fields.Float(allow_none=True)
    past_due_total = fields.Float(allow_none=True)
    past_due_30 = fields.Float(allow_none=True)
    past_due_60 = fields.Float(allow_none=True)
    past_due_90 = fields.Float(allow_none=True)
    past_due_180 = fields.Float(allow_none=True)
    past_due_360 = fields.Float(allow_none=True)
    past_due_past_360 = fields.Float(allow_none=True)
    loss_total = fields.Float(allow_none=True)
    loss_12 = fields.Float(allow_none=True)
    loss_48 = fields.Float(allow_none=True)
    credit_portfolio = fields.Float(allow_none=True)
    total_responsibility = fields.Float(allow_none=True)
    credit_limit_total = fields.Float(allow_none=True)
    credit_limit_360 = fields.Float(allow_none=True)
    credit_limit_past_360 = fields.Float(allow_none=True)
    guarantor_indirect_risk = fields.Float(allow_none=True)
    risk_total = fields.Float(allow_none=True)
    payload = fields.Dict(allow_none=True)

    @pre_load
    def log_received_data(self, data, **kwargs) -> Dict[Any, Any]:
        logger.debug(f"Request Data received is: {data}")
        return data

    @post_load
    def make_data(self, data, **kwargs) -> BancoCentralData:
        logger.debug(f"Deserialized Data received is: {data}")
        new_data = BancoCentralData(**data)
        new_data.datasource_base_url = BancoCentral.base_url
        return new_data

    class Meta:
        unknown = EXCLUDE


@dataclass
class BancoCentral(BaseSnatch):
    default_timeout: int = 10
    default_max_periods: int = 0
    base_url_key: str = "snatch.datasource_banco_central_url"
    authorization_token_key: str = "snatch.banco_central_secret_token"
    serializer_class: Type[Schema] = BancoCentralSerializer
