import pytest
from common.models import Result
from common.huobi.service import HuobiService
from common.huobi.constants import TradeType
from common.huobi.exceptions import HuobiAPIException


@pytest.mark.asyncio
async def test_cancel_all_orders(huobi_service: HuobiService, logger):
    try:
        resp: Result = await huobi_service.cancel_all_orders(TradeType.FUTURE, symbol='fil')
        logger.info(resp)
    except HuobiAPIException as e:
        if e.error_code != 1051:
            raise e

    try:
        resp: Result = await huobi_service.cancel_all_orders(TradeType.COIN_M, contract_code='fil-usd')
        logger.info(resp)
    except HuobiAPIException as e:
        if e.error_code != 1051:
            raise e

