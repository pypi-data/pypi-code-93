from fqsdfqsdfqsdfqsd.wallets.wallet import Wallet


class InvestorWallet(Wallet):
    _instances = set()

    def __init__(self, USDC_balance=1000):
        super().__init__(USDC_balance=USDC_balance)
        self.UT_balance = None
        self._instances.add(self)

    @classmethod
    def get_instances(cls):
        return cls._instances

    @classmethod
    def del_instance(cls, instance):
        cls._instances.remove(instance)