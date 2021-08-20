from binance.client import Client, AsyncClient


class Wallet:
    def __init__(self, client: Client = None, async_client: AsyncClient = None):
        self.client = client
        self.async_client = async_client

    def get_spot_balance(self, asset: str = None) -> dict:
        """
        现货账户余额
        :param asset:
        :return:
        {
            "asset": "KMD",
            "free": "0.00000000",
            "locked": "0.00000000"
        }
        """
        rst = self.client.get_account()
        # list -> dict
        balances = {item['asset']: item for item in rst['balances']}
        if asset:
            return balances[asset.upper()]
        return balances

    async def async_get_spot_balance(self, asset: str = None) -> dict:
        rst = await self.async_client.get_account()
        # list -> dict
        balances = {item['asset']: item for item in rst['balances']}
        if asset:
            return balances[asset.upper()]
        return balances

    def get_coin_future_balance(self, asset: str = None) -> dict:
        """
        币本位账户余额
        {
            "accountAlias": "SgsR",    // 账户唯一识别码
            "asset": "BTC",     // 资产
            "balance": "0.00250000",    // 账户余额
            "withdrawAvailable": "0.00250000", // 最大可提款金额,同`GET /dapi/account`中"maxWithdrawAmount"
            "crossWalletBalance": "0.00241969", // 全仓账户余额
            "crossUnPnl": "0.00000000", // 全仓持仓未实现盈亏
            "availableBalance": "0.00241969",    // 可用下单余额
            "updateTime": 1592468353979
        }
        """
        rst = self.client.futures_coin_account_balance()
        # list -> dict
        balances = {item['asset']: item for item in rst}

        if asset:
            return balances[asset]
        return balances

    async def async_get_coin_future_balance(self, asset: str = None) -> dict:
        rst = await self.async_client.futures_coin_account_balance()
        # list -> dict
        balances = {item['asset']: item for item in rst}

        if asset:
            return balances[asset]
        return balances

