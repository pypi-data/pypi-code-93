import uuid
from fqsdfqsdfqsdfqsd.tokens import UT, RT

class Wallet:
    def __init__(self, USDC_balance=1000):
        self.wallet_address = str(uuid.uuid4())
        self.USDC_balance = USDC_balance
        self.UT_balance = list()
        self.RT_balance = list()
        self.IT_balance = 0

    def del_UT(self, instance):
        try:
            self.UT_balance.remove(instance)
            UT.del_instance(instance)
        except:
            pass

    def del_RT(self, instance):
        try:
            self.RT_balance.remove(instance)
            RT.del_instance(instance)
        except:
            pass