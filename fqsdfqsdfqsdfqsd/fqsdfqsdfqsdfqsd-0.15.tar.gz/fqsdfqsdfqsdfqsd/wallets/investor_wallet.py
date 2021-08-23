from fqsdfqsdfqsdfqsd.wallets.wallet import Wallet
from fqsdfqsdfqsdfqsd.contracts import MatchContract

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

    @classmethod
    def withdraw_IT(cls, IT_amount_to_withdraw, reserve):
        investor_wallets = cls.get_instances()
        for investor_wallet in investor_wallets:
            investor_wallet_IT_balance = investor_wallet.IT_balance
            if investor_wallet_IT_balance > IT_amount_to_withdraw:
                IT_amount_to_withdraw_from_wallet = IT_amount_to_withdraw
            else:
                IT_amount_to_withdraw_from_wallet = investor_wallet_IT_balance

            continue_withdrawing = MatchContract.withdraw_IT(IT_amount_to_withdraw_from_wallet, investor_wallet, reserve)
            IT_amount_to_withdraw -= IT_amount_to_withdraw_from_wallet
            print("-----------------")
            print(f"continue withdrawing {continue_withdrawing}")
            print("-----------------")
            if not continue_withdrawing or IT_amount_to_withdraw == 0:
                break
