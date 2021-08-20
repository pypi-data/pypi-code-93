# coding: utf8


__all__ = ["DoubleBarrierInfo"]


from refinitiv.dataplatform.content.ipa.instrument._definition import ObjectDefinition


class DoubleBarrierInfo(ObjectDefinition):
    """"""

    def __init__(self, in_or_out=None, level=None, rebate_amount=None):
        super().__init__()
        self.in_or_out = in_or_out
        self.level = level
        self.rebate_amount = rebate_amount

    @property
    def in_or_out(self):
        """
        In/Out property of the barrier option
        :return: string
        """
        return self._get_parameter("inOrOut")

    @in_or_out.setter
    def in_or_out(self, value):
        self._set_parameter("inOrOut", value)

    @property
    def level(self):
        """
        Barrier of the barrier option
        :return: double
        """
        return self._get_parameter("level")

    @level.setter
    def level(self, value):
        self._set_parameter("level", value)

    @property
    def rebate_amount(self):
        """
        Rebate of the barrier option
        :return: double
        """
        return self._get_parameter("rebateAmount")

    @rebate_amount.setter
    def rebate_amount(self, value):
        self._set_parameter("rebateAmount", value)
