import re

from common.huobi.client import AsyncClient
from common.huobi.constants import TradeType
from common.models import Result


class AccountService:
    def __init__(self, client: AsyncClient):
        self.client = client

    async def account_info(self, trade_type, symbol: str):
        # symbol 可能有如下格式: btc-usd,btc_nw,btc210420
        if "_" in symbol:
            symbol = symbol.split('_')[0]
        else:
            match_value = re.match('^([a-zA-Z]+)([0-9]+)$', symbol)
            if match_value:
                symbol = match_value.groups()[0]

        rst: Result
        if trade_type == TradeType.FUTURE:
            # symbol: btc,eth,...
            rst = await self.client.future_account_info(symbol)
        elif trade_type == TradeType.COIN_M:
            # symbol: btc-usd, eth-usd,...
            rst = await self.client.coin_margined_account_info(contract_code=symbol)
        else:
            raise Exception(f"unsupported trade type: {trade_type}")
        return rst.data

    async def transfer(self, symbol, from_type, to_type, amount):
        """
        资金划转
        如果不涉及币币账户，都需要币币作为中转
        """
        assert from_type != to_type

        if from_type == TradeType.SPOT:
            if to_type == TradeType.FUTURE:
                return await self.client.future_transfer(symbol, amount, transfer_type="pro-to-futures")
            elif to_type == TradeType.COIN_M:
                return await self.client.coin_margined_transfer("spot", "swap", symbol, amount)
        elif from_type == TradeType.FUTURE:
            if to_type == TradeType.SPOT:
                return await self.client.future_transfer(symbol, amount, transfer_type="futures-to-pro")
            elif to_type == TradeType.COIN_M:
                await self.transfer(symbol, from_type, TradeType.SPOT, amount)
                return await self.transfer(symbol, TradeType.SPOT, to_type, amount)
        elif from_type == TradeType.COIN_M:
            if to_type == TradeType.SPOT:
                return await self.client.coin_margined_transfer("swap", "spot", symbol, amount)
            elif to_type == TradeType.FUTURE:
                await self.transfer(symbol, from_type, TradeType.SPOT, amount)
                return await self.transfer(symbol, TradeType.SPOT, to_type, amount)


