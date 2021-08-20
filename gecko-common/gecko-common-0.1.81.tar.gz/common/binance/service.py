import logging

from binance.client import AsyncClient, BaseClient
from .constant import TradeType


TransferTypeDict = {
    (TradeType.SPOT, TradeType.COIN_M): AsyncClient.SPOT_TO_COIN_FUTURE,
    (TradeType.SPOT, TradeType.USD_M): AsyncClient.SPOT_TO_USDT_FUTURE,
    (TradeType.COIN_M, TradeType.SPOT): AsyncClient.COIN_FUTURE_TO_SPOT,
    (TradeType.USD_M, TradeType.SPOT): AsyncClient.USDT_FUTURE_TO_SPOT,
}


class BinanceService:
    def __init__(self, client: AsyncClient):
        self.client = client

    async def account_info(self, trade_type, symbol: str) -> (float, float):
        """
        返回total, available
        """
        if trade_type == TradeType.SPOT:
            rst = self.client.get_account()
            if symbol:
                balance_info = [item for item in rst['balances'] if item['asset'] == symbol]
                if not balance_info:
                    return 0, 0
                return float(balance_info[0]['free']) + float(balance_info[0]['locked']), float(balance_info[0]['free'])
        elif trade_type == TradeType.COIN_M:
            rst = self.client.futures_coin_account()
            balance_info = [item for item in rst['assets'] if item['asset'] == symbol]
            if not balance_info:
                return 0, 0
            return float(balance_info[0]['walletBalance']), float(balance_info[0]['maxWithdrawAmount'])
        else:
            rst = self.client.futures_account()
            balance_info = [item for item in rst['assets'] if item['asset'] == symbol]
            if not balance_info:
                return 0, 0
            return float(balance_info[0]['walletBalance']), float(balance_info[0]['maxWithdrawAmount'])

    async def transfer(self, symbol, from_type, to_type, amount):
        """
        资金划转
        如果不涉及币币账户，都需要币币作为中转
        """
        assert from_type != to_type

        if from_type == TradeType.SPOT:
            return await self.client.universal_transfer(
                type=TransferTypeDict[(from_type, to_type)], asset=symbol, amount=str(amount)
            )
        elif from_type == TradeType.COIN_M:
            if to_type == TradeType.SPOT:
                return await self.client.universal_transfer(
                    type=TransferTypeDict[(from_type, to_type)], asset=symbol, amount=str(amount)
                )
            else:
                await self.transfer(symbol, from_type, TradeType.SPOT, amount)
                return await self.transfer(symbol, TradeType.SPOT, to_type, amount)
        elif from_type == TradeType.USD_M:
            if to_type == TradeType.SPOT:
                return await self.client.universal_transfer(
                    type=TransferTypeDict[(from_type, to_type)], asset=symbol, amount=str(amount)
                )
            else:
                await self.transfer(symbol, from_type, TradeType.SPOT, amount)
                return await self.transfer(symbol, TradeType.SPOT, to_type, amount)

    async def position_info(self, trade_type, symbol):
        data = None
        if trade_type == TradeType.COIN_M:
            rst = await self.client.futures_coin_position_information(pair=symbol)
            data = [item for item in rst if item['symbol'] == symbol]
        elif trade_type == TradeType.USD_M:
            rst = await self.client.futures_position_information(symbol=symbol)
            data = [item for item in rst if item['symbol'] == symbol]

        if not data:
            return None
        else:
            return data[0]

    async def close_all_position(self, trade_type, symbol):
        position_info = await self.position_info(trade_type, symbol)
        amount = int(position_info['positionAmt'])
        if amount > 0:
            side = BaseClient.SIDE_SELL
        else:
            side = BaseClient.SIDE_BUY
        params = {
            "symbol": symbol,
            "side": side,
            "type": BaseClient.ORDER_TYPE_MARKET,
            "quantity": abs(amount)
        }
        if trade_type == TradeType.COIN_M:
            func = self.client.futures_coin_create_order
        else:
            func = self.client.futures_create_order
        try:
            await func(**params)
        except Exception as e:
            logging.error(e)

    async def cancel_all_orders(self, trade_type, symbol):
        if trade_type == TradeType.COIN_M:
            func = self.client.futures_coin_cancel_all_open_orders
        elif trade_type == TradeType.USD_M:
            func = self.client.futures_cancel_all_open_orders
        else:
            func = self.client.cancel_all_orders

        await func(symbol=symbol)


