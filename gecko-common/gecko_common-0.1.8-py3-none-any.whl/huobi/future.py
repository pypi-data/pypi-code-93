from huobi.client.future import FutureClient
from huobi.utils.dict_util import remove_key


class Future:
    def __init__(self, key: str, secret: str):
        params = {"api_key": key, "secret_key": secret, "init_log": True}
        self.client = FutureClient(**params)

    def get_contract_info(self, symbol=None, contract_type=None, contract_code=None):
        """
        参数名称         参数类型  必填    描述
        symbol          string  false   "BTC","ETH"...
        contract_type   string  false   合约类型: this_week:当周 next_week:下周 quarter:季度
        contract_code   string  false   BTC181228
        备注：如果contract_code填了值，那就按照contract_code去查询，如果contract_code 没有填值，则按照symbol+contract_type去查询
        """
        return self.client.get_contract_info(**remove_key(locals()))

