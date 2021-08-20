from huobi.client.account import AccountClient
from huobi.client.coin_margined_swap import CoinMarginedSwapClient
from huobi.client.future import FutureClient
from huobi.constant.definition import AccountType
from common.dict_util import remove_key


class Wallet:
    def __init__(self, key: str, secret: str):
        params = {"api_key": key, "secret_key": secret, "init_log": True}
        self.account_client = AccountClient(**params)
        self.coin_margined_swap_client = CoinMarginedSwapClient(**params)
        self.future_client = FutureClient(**params)
        self.accounts = None

    def get_account_id(self, account_type: AccountType) -> int:
        if self.accounts is None:
            accounts = self.account_client.get_accounts()
            self.accounts = {account.type: account for account in accounts}
        return self.accounts[account_type].id

    def get_spot_balance(self, asset: str = None) -> dict:
        """
        现货账户余额
        """
        resp = self.account_client.get_balance(self.get_account_id(AccountType.SPOT))
        balances = {item.currency: item for item in resp if item.balance != '0'}
        if asset:
            return balances.get(asset)
        return balances

    def get_coin_margined_swap_balance_valuation(self, valuation_asset: str = "BTC"):
        """
        币本位账户资产估值
        """
        resp = self.coin_margined_swap_client.get_balance_valuation(valuation_asset)
        return resp

    def get_coin_margined_swap_position(self, contract_code: str = None):
        """
        币本位账户持仓
        contract_code	false	string	合约代码		支持大小写，"BTC-USD"... ,如果缺省，默认返回所有合约
        """
        return self.coin_margined_swap_client.get_swap_position_info(contract_code)

    def get_coin_margined_swap_account_info(self, contract_code: str = None):
        """
        币本位账户信息
        contract_code	false	string	支持大小写, "BTC-USD"... ,如果缺省，默认返回所有合约
        """
        return self.coin_margined_swap_client.get_swap_account_info(contract_code)

    def get_contract_balance_valuation(self, valuation_asset='BTC'):
        """
        交割合约账户估值
        valuation_asset	false	string	资产估值币种，即按该币种为单位进行估值，不填默认"BTC"	"BTC","USD","CNY","EUR","GBP","VND","HKD","TWD","MYR","SGD","KRW","RUB","TRY"
        """
        return self.future_client.get_contract_balance_valuation(valuation_asset)

    def get_contract_account_info(self, symbol=None):
        """
        获取交割合约账户信息
        symbol	false	string	品种代码		支持大小写,"BTC","ETH"...如果缺省，默认返回所有品种
        """
        return self.future_client.get_contract_account_info(**remove_key(locals()))

    def get_contract_position_info(self, symbol=None):
        """
        获取交割合约账户持仓信息
        symbol	false	string	品种代码		支持大小写,""BTC","ETH"...如果缺省，默认返回所有品种
        备注:
        如果有某个品种在结算中，不带请求参数去查询持仓，
        会返回错误码1080(1080 In settlement or delivery. Unable to get positions of some contracts. )。
        建议您带上请求参数去查询持仓，避免报错查询不到持仓。
        """
        return self.future_client.get_contract_position_info(**remove_key(locals()))


