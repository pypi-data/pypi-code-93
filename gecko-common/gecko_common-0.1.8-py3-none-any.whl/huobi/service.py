import logging
import re
from common.huobi.client import AsyncClient
from common.huobi.constants import TradeType, OrderPriceType
from common.huobi.utils import reverse_direction
from common.huobi.exceptions import HuobiAPIException


class HuobiService:
    def __init__(self, client: AsyncClient):
        self.client = client

    async def close_all_position(self, trade_type, contract_code):
        """
        关闭所有仓位, 使用闪电平仓模式
        """
        position_info = await self.position_info(trade_type, contract_code)
        if trade_type == TradeType.FUTURE:
            func = self.client.future_lightning_close_position
        elif trade_type == TradeType.COIN_M:
            func = self.client.coin_margined_lightning_close_position
        else:
            raise Exception(f"unsupported trade type: {trade_type}")

        for position in position_info:
            params = {
                'contract_code': position['contract_code'],
                'volume': int(position['available']),
                'direction': reverse_direction(position['direction']),
                "order_price_type": OrderPriceType.LIGHTNING
            }
            logging.debug(f"闪电平仓: {params}")
            await func(**params)

    async def position_info(self, trade_type, contract_code) -> list:
        """
        获取当前仓位信息
        """
        if trade_type == TradeType.FUTURE:
            symbol = re.match("^([a-zA-Z]+)[0-9]+$", contract_code).group(1)
            rst = await self.client.future_position_info(symbol)
            data = [e for e in rst.data if e['contract_code'] == contract_code]
        elif trade_type == TradeType.COIN_M:
            rst = await self.client.coin_margined_position_info(contract_code)
            data = [e for e in rst.data if e['contract_code'] == contract_code]
        else:
            raise Exception(f"unsupported trade type: {trade_type}")
        return data

    async def cancel_all_orders(self, trade_type, symbol=None, contract_code=None, contract_type=None, direction=None,
                                offset=None):
        """
        全部撤单
        """
        if trade_type == TradeType.FUTURE:
            func = self.client.future_cancel_all
            if symbol is None and contract_code is not None:
                symbol = re.match("^([a-zA-Z]+)[0-9]+$", contract_code).group(1)
            params = {
                'symbol': symbol,
                'contract_code': contract_code,
                'contract_type': contract_type,
                'direction': direction,
                'offset': offset
            }
        elif trade_type == TradeType.COIN_M:
            func = self.client.coin_margined_cancel_all
            params = {
                'contract_code': contract_code,
                'direction': direction,
                'offset': offset
            }
        else:
            raise Exception(f"unsupported trade type: {trade_type}")
        try:
            return await func(**params)
        except HuobiAPIException as e:
            if e.error_code != 1051:
                raise e

    async def cancel_order(self, trade_type, order_id, symbol=None, contract_code=None):
        params = {"order_id": order_id}
        if trade_type == TradeType.FUTURE:
            func = self.client.future_cancel_order
            params["symbol"] = symbol
        elif trade_type == TradeType.COIN_M:
            func = self.client.coin_margined_cancel_order
            params["contract_code"] = contract_code
        elif trade_type == TradeType.USD_M:
            func = self.client.usd_margined_cancel_order
            params['contract_code'] = contract_code
        else:
            func = self.client.spot_cancel_order
        # Result(
        # code=200,
        # status='ok',
        # msg='',
        # data={'errors': [{'order_id': '872859639523352576', 'err_code': 1063, 'err_msg': 'The order has been executed.'}],
        # 'successes': ''}
        # )
        rst = await func(**params)
        return rst
