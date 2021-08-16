from fqsdfqsdfqsdfqsd.tokens.NFT import NFT


class RT(NFT):
    _instances = set()

    def __init__(self, USDC_amount, wallet):
        super().__init__(USDC_amount, wallet)
        self._instances.add(self)

    @classmethod
    def get_instances(cls):
        return cls._instances

    @classmethod
    def del_instance(cls, instance):
        cls._instances.remove(instance)

    @classmethod
    def get_RT_in_circulation(cls):
        RTs = cls._instances
        total_amount = 0
        for rt in RTs:
            total_amount += rt.USDC_amount

        return total_amount