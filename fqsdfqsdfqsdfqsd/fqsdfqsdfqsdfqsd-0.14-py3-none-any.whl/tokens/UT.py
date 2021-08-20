from fqsdfqsdfqsdfqsd.tokens.NFT import NFT


class UT(NFT):
    _instances = set()

    def __init__(self, USDC_amount, wallet, deal):
        super().__init__(USDC_amount, wallet)
        self.deal = deal
        self._instances.add(self)

    @classmethod
    def get_instances(cls):
        return cls._instances

    @classmethod
    def del_instance(cls, instance):
        cls._instances.remove(instance)

    @classmethod
    def get_UT_in_circulation(cls):
        UTs = cls._instances
        total_amount = 0
        for ut in UTs:
            total_amount += ut.USDC_amount

        return total_amount
